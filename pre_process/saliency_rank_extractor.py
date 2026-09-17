"""
Docstring for sr-model1.dataset_builder.py.saliency_rank_extractor
Build saliency ranking dataset from saliency maps
"""
import torch
import os
import numpy as np
import cv2
from PIL import Image
import json
from scipy.stats import mode
import cv2
from pycocotools import mask as maskUtils
from tqdm import tqdm
torch.backends.cudnn.benchmark = True

device = torch.device("cuda:1" if torch.cuda.is_available() else "cpu")
splits = {"test":"test", "train":"train", "val":"val"}
# dataset_dir = "/data/research/zaima/dataset/Dataset/SIFR/SIFR_dataset"
# dataset_dir = "/home/zaimaz/Desktop/research1/QAGNet/Dataset/IRSR_ASSR"
dataset_dir = "/data/research/zaima/dataset/Dataset/ASSR"
image_store = "images"
sal_map_store = "gt"
ranks_order_store = "rank_order"

coco_ann_file = "/data/research/zaima/dataset/Dataset/coco_annotations/instances_train2014.json"
with open(coco_ann_file, "r") as f:
    coco = json.load(f)

def segmentation_to_mask(segmentation, height, width):
    """
    Convert any COCO segmentation (polygon, RLE, uncompressed RLE)
    into a binary mask of shape (H, W).
    """

    # Case 1: POLYGON segmentation
    if isinstance(segmentation, list):
        # it may be a list of polygon lists
        rles = maskUtils.frPyObjects(segmentation, height, width)
        rle = maskUtils.merge(rles)
        m = maskUtils.decode(rle)
        return m.astype(np.uint8)

    # Case 2: RLE segmentation (compressed or uncompressed)
    elif isinstance(segmentation, dict) and "counts" in segmentation:
        # If counts is a list → UNCOMPRESSED RLE → convert
        if isinstance(segmentation["counts"], list):
            rle = maskUtils.frPyObjects(segmentation, height, width)
        else:
            # counts is a string → already compressed
            rle = segmentation

        m = maskUtils.decode(rle)
        return m.astype(np.uint8)

    else:
        raise ValueError(f"Unknown segmentation type: {type(segmentation)}")
    
def mask_iou(mask1, mask2):
    inter = np.logical_and(mask1, mask2).sum()
    union = np.logical_or(mask1, mask2).sum()
    if union == 0:
        return 0.0
    return inter / union

from pycocotools import mask as coco_mask
def ann_to_mask(ann, H, W):
    rle = coco_mask.frPyObjects(ann["segmentation"], H, W)
    mask = coco_mask.decode(rle)

    if mask.ndim == 3:
        mask = np.any(mask, axis=2)

    return mask.astype(bool)



def extract_masks_from_sal_map(image_id, image_dir):
    img = np.array(Image.open(image_dir).convert("L"))

    unique_vals = [v for v in np.unique(img) if v > 0]

    objects = {image_id: []}
    next_id = 1

    for val in unique_vals:
        mask = (img == val).astype(np.uint8)
        area = int(mask.sum())
        if area == 0:
            continue

        mask_cv = (mask * 255).astype(np.uint8)
        contours, _ = cv2.findContours(mask_cv, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        coco_polys = []
        all_points = []

        for cnt in contours:
            if len(cnt) >= 3:
                poly = cnt.reshape(-1, 2).astype(float)
                coco_polys.append(poly.flatten().tolist())
                all_points.append(poly)

        if not coco_polys:
            continue

        all_points = np.vstack(all_points)
        x_min = float(all_points[:, 0].min())
        y_min = float(all_points[:, 1].min())
        x_max = float(all_points[:, 0].max())
        y_max = float(all_points[:, 1].max())

        bbox = [x_min, y_min, x_max - x_min, y_max - y_min]

        obj = {
            "segmentation": coco_polys,
            "area": area,
            "iscrowd": 0,
            "image_id": image_id,
            "bbox": bbox,
            "category_id": 0,
            "id": next_id
        }

        objects[image_id].append(obj)
        next_id += 1

    return objects


    
def extract_saliency_rank_order(image_dir, objects):
    """
    Returns:
        rank_order: indices within the valid-mask list, sorted by descending saliency
        valid_masks: original mask indices that were retained (in original order)
        invalid_masks: original mask indices that were removed (in original order)
    """
    print(image_dir)
    img = np.array(Image.open(image_dir).convert("L"))
    H, W = img.shape

    valid_entries = []   # (original_idx, mode_value)
    invalid_masks = []   # original indices only

    for idx, object in enumerate(objects):
        seg = object['segmentation'] 
        # print(seg)
        full_mask = segmentation_to_mask(seg, H, W)
        vals = img[full_mask.astype(bool)]

        if len(vals) == 0:
            invalid_masks.append(idx)
            continue

        mode_val = mode(vals, keepdims=False).mode

        if mode_val > 0:
            valid_entries.append((idx, int(mode_val)))
        else:
            invalid_masks.append(idx)

    # valid mask original indices (in original order)
    valid_masks = [x[0] for x in valid_entries]

    # Sort valid entries by saliency DESCENDING
    sorted_valid = sorted(
        enumerate(valid_entries),   # enumerate so we keep valid-list index
        key=lambda x: x[1][1],      # sort by mode_val
        reverse=True
    )

    # rank_order: indices within valid list
    rank_order = [i for (i, entry) in sorted_valid]
    print(rank_order)

    return rank_order, valid_masks, invalid_masks


import numpy as np
import cv2
import torch
from PIL import Image
from transformers import MaskFormerImageProcessor, MaskFormerForInstanceSegmentation

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

_MASKFORMER_PROCESSOR = None
_MASKFORMER_MODEL = None

def _load_maskformer(model_name="facebook/maskformer-swin-base-coco"):
    global _MASKFORMER_PROCESSOR, _MASKFORMER_MODEL

    if _MASKFORMER_PROCESSOR is None or _MASKFORMER_MODEL is None:
        _MASKFORMER_PROCESSOR = MaskFormerImageProcessor.from_pretrained(model_name)
        _MASKFORMER_MODEL = MaskFormerForInstanceSegmentation.from_pretrained(model_name).to(device)
        _MASKFORMER_MODEL.eval()

    return _MASKFORMER_PROCESSOR, _MASKFORMER_MODEL
maskformer_processor, maskformer_model = _load_maskformer()

def _binary_mask_to_coco_polygons(mask):
    mask = mask.astype(np.uint8)
    if mask.max() == 0:
        return [], None

    mask_cv = (mask * 255).astype(np.uint8)
    contours, _ = cv2.findContours(mask_cv, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    coco_polys = []
    all_points = []

    for cnt in contours:
        if len(cnt) < 3:
            continue

        poly = cnt.reshape(-1, 2).astype(float)

        if poly.shape[0] < 3:
            continue

        coco_polys.append(poly.flatten().tolist())
        all_points.append(poly)

    if not coco_polys:
        return [], None

    all_points = np.vstack(all_points)
    x_min = float(all_points[:, 0].min())
    y_min = float(all_points[:, 1].min())
    x_max = float(all_points[:, 0].max())
    y_max = float(all_points[:, 1].max())

    bbox = [x_min, y_min, x_max - x_min, y_max - y_min]
    return coco_polys, bbox


import numpy as np
import torch
from PIL import Image

def _mask_to_bbox(mask):
    ys, xs = np.where(mask > 0)
    if len(xs) == 0 or len(ys) == 0:
        return None
    x_min = float(xs.min())
    y_min = float(ys.min())
    x_max = float(xs.max())
    y_max = float(ys.max())
    return [x_min, y_min, x_max - x_min + 1, y_max - y_min + 1]


def maskformer_masks(
    image_id,
    image,
    model_name="facebook/maskformer-swin-base-coco",
    score_threshold=0.5,
    keep_category_id=True
):
    processor, model = maskformer_processor, maskformer_model

    if isinstance(image, str):
        pil_img = Image.open(image).convert("RGB")
    elif isinstance(image, Image.Image):
        pil_img = image.convert("RGB")
    elif isinstance(image, np.ndarray):
        if image.ndim != 3 or image.shape[2] != 3:
            raise ValueError("NumPy image must have shape (H, W, 3)")
        pil_img = Image.fromarray(image.astype(np.uint8)).convert("RGB")
    else:
        raise TypeError("image must be a path, PIL.Image, or numpy RGB array")

    H, W = pil_img.size[1], pil_img.size[0]

    inputs = processor(images=pil_img, return_tensors="pt")
    inputs = {k: v.to(device) for k, v in inputs.items()}

    with torch.no_grad():
        with torch.cuda.amp.autocast():
            outputs = model(**inputs)

    result = processor.post_process_panoptic_segmentation(
        outputs,
        target_sizes=[(H, W)],
        threshold=score_threshold
    )[0]

    segmentation_map = result["segmentation"].cpu().numpy()
    segments_info = result["segments_info"]

    objects = {image_id: []}
    next_id = 1

    for seg in segments_info:
        seg_id = seg["id"]
        label_id = int(seg["label_id"])
        score = float(seg.get("score", 1.0))

        if score < score_threshold:
            continue

        mask = (segmentation_map == seg_id).astype(np.uint8)
        area = int(mask.sum())

        if area == 0:
            continue

        bbox = _mask_to_bbox(mask)
        if bbox is None:
            continue

        obj = {
            "segmentation": [],
            "area": area,
            "iscrowd": 0,
            "image_id": image_id,
            "bbox": bbox,
            "category_id": label_id if keep_category_id else 0,
            "id": next_id
        }

        objects[image_id].append(obj)
        next_id += 1

    return objects

def bbox_iou(box1, box2):
    x1, y1, w1, h1 = box1
    x2, y2, w2, h2 = box2

    x1_max = x1 + w1
    y1_max = y1 + h1
    x2_max = x2 + w2
    y2_max = y2 + h2

    inter_x1 = max(x1, x2)
    inter_y1 = max(y1, y2)
    inter_x2 = min(x1_max, x2_max)
    inter_y2 = min(y1_max, y2_max)

    inter_w = max(0.0, inter_x2 - inter_x1)
    inter_h = max(0.0, inter_y2 - inter_y1)
    inter_area = inter_w * inter_h

    area1 = max(0.0, w1) * max(0.0, h1)
    area2 = max(0.0, w2) * max(0.0, h2)

    union = area1 + area2 - inter_area
    if union <= 0:
        return 0.0

    return inter_area / union


def attach_maskformer_bboxes(seg_info, seg_info_maskformer, image_id, iou_threshold=0.0):
    """
    Replace saliency bbox with best matching MaskFormer bbox using bbox IoU.
    Does NOT use MaskFormer segmentation.
    """
    if image_id not in seg_info or len(seg_info[image_id]) == 0:
        return []

    if image_id not in seg_info_maskformer or len(seg_info_maskformer[image_id]) == 0:
        return seg_info[image_id]

    sal_objs = seg_info[image_id]
    mf_objs = seg_info_maskformer[image_id]

    updated_objs = []

    for seg_entry in sal_objs:
        sal_bbox = seg_entry["bbox"]

        best_iou = -1.0
        best_bbox = sal_bbox

        for mf_entry in mf_objs:
            mf_bbox = mf_entry["bbox"]
            iou = bbox_iou(sal_bbox, mf_bbox)

            if iou > best_iou:
                best_iou = iou
                best_bbox = mf_bbox

        new_entry = dict(seg_entry)
        if best_iou >= iou_threshold:
            new_entry["bbox"] = best_bbox

        updated_objs.append(new_entry)

    return updated_objs


def extract_objects(image_dir, rgb_dir, coco):
    image_name = os.path.splitext(os.path.basename(image_dir))[0]
    image_id = None

    for img in coco.get("images", []):
        if os.path.splitext(img["file_name"])[0] == image_name:
            image_id = img["id"]
            break

    seg_info = extract_masks_from_sal_map(image_id=image_id, image_dir=image_dir)
    # seg_info_maskformer = maskformer_masks(image_id=image_id, image=rgb_dir)

    if image_id not in seg_info or len(seg_info[image_id]) == 0:
        return []

    H, W = Image.open(image_dir).size[::-1]

    objects = []

    anns = [ann for ann in coco.get("annotations", []) if ann["image_id"] == image_id]

    # seg_info_with_mf_bbox = attach_maskformer_bboxes(
    #     seg_info=seg_info,
    #     seg_info_maskformer=seg_info_maskformer,
    #     image_id=image_id,
    #     iou_threshold=0.0
    # )

    # --------------------------------------------------
    # CASE 1: NO annotations → directly use seg_info,
    # but bbox comes from maskformer match
    # --------------------------------------------------
    if len(anns) == 0:
        for idx, seg_entry in enumerate(seg_info):
            obj = {
                "segmentation": seg_entry["segmentation"],
                "area": seg_entry["area"],
                "bbox": seg_entry["bbox"],
                "iscrowd": 0,
                "image_id": image_id,
                "category_id": -1,
                "id": seg_entry.get("id", idx),
                "matched_iou": None
            }
            objects.append(obj)

        return objects

    # --------------------------------------------------
    # CASE 2: annotations available → IoU matching
    # segmentation/area from saliency map, bbox from maskformer match
    # --------------------------------------------------
    sal_entries = seg_info[image_id]

    sal_masks = [
        segmentation_to_mask(seg_entry["segmentation"], H, W).astype(bool)
        for seg_entry in sal_entries
    ]

    ann_masks = [
        ann_to_mask(ann, H, W)
        for ann in anns
    ]

    for ann, ann_mask in zip(anns, ann_masks):
        ann_bbox = ann["bbox"]

        best_iou = 0.0
        best_idx = -1

        for idx, seg_entry in enumerate(sal_entries):
            if bbox_iou(seg_entry["bbox"], ann_bbox) < 0.1:
                continue

            iou = mask_iou(sal_masks[idx], ann_mask)

            if iou > best_iou:
                best_iou = iou
                best_idx = idx

        if best_iou < 0.8 or best_idx < 0:
            continue

        matched = seg_info[best_idx]

        obj = {
            "segmentation": matched["segmentation"],
            "area": matched["area"],
            "bbox": matched["bbox"],
            "iscrowd": ann.get("iscrowd", 0),
            "image_id": image_id,
            "category_id": ann.get("category_id", -1),
            "id": ann.get("id", -1),
            "matched_iou": best_iou
        }

        objects.append(obj)

    return objects


def save_json(data, file):
    with open(file, "w") as f:
        json.dump(data, f, indent=2)

split = splits["test"]
images_dir = os.path.join(dataset_dir, image_store, split)
image_files = os.listdir(images_dir)

save_test_anns = os.path.join(dataset_dir, f"obj_seg_data_{split}.json")
save_rank_order_dir = os.path.join(dataset_dir, ranks_order_store, split)

test_anns = []
for img_file in tqdm(image_files, desc="Processing images"):
    basename = os.path.splitext(img_file)[0]
    image_dir = os.path.join(dataset_dir, image_store, split, img_file)
    sal_map_dir = os.path.join(dataset_dir, sal_map_store, split, f"{basename}.png")
    if not os.path.exists(sal_map_dir):
        continue
    # print(sal_map_dir)
    objects = extract_objects(sal_map_dir, image_dir, coco=coco)
    
    saliency_ranks, valid_objects, invalid_objects = extract_saliency_rank_order(sal_map_dir, objects)
    anns = {
        "img": basename,
        "object_data": objects
    }
    test_anns.append(anns)
    rank_order_info = {
        "image_id": basename, 
        "rank_order": saliency_ranks
    }
    rank_order_fname = os.path.join(save_rank_order_dir, f"{basename}.json")
    save_json(rank_order_info, rank_order_fname)
    # break
    
    
    # print(f"Filename: {basename}, saliency_ranks: {saliency_ranks} of {len(valid_objects)} objects")

save_json(test_anns, save_test_anns)



    





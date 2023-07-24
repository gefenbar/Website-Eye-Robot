import torch
import torchvision
import cv2
import matplotlib.pyplot as plt

def load_model(weights="SSD300_VGG16_Weights.DEFAULT"):
    # Load the pre-trained SSD model with a ResNet backbone
    model = torchvision.models.detection.ssd300_vgg16(weights=weights)
    model.eval()
    return model

def detect_objects(model, image_path):
    # Load and preprocess the image
    image = cv2.imread(image_path)
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    image_tensor = torchvision.transforms.functional.to_tensor(image_rgb)
    image_tensor = image_tensor.unsqueeze(0)
    
    # Make predictions using the model
    with torch.no_grad():
        predictions = model(image_tensor)
    
    # Extract bounding boxes and labels of detected objects
    boxes = predictions[0]['boxes'].tolist()
    labels = predictions[0]['labels'].tolist()
    scores = predictions[0]['scores'].tolist()
   
    for i in range(len(boxes)):
        if scores[i]>0.3: 
            print(f'labels[i]: ', labels[i])
            print(f'scores[i]: ', scores[i])
    # Filter out detections of objects
    object_boxes = [boxes[i] for i in range(len(boxes)) if labels[i]>=1 and labels[i]!=84 and labels[i]!=61 and labels[i]!=67 and labels[i]!=72 and labels[i]!=73  and scores[i] > 0.3]
    
    hide_detected_objects(image_path,object_boxes)


def hide_detected_objects(image_path, boxes):
    # Load the image
    image = cv2.imread(image_path)
    
    # Create a mask to hide objects
    mask = image.copy()
    mask[:] = (0, 0, 0)  # Set the mask to black
    
    # Expand the bounding boxes to mask a larger area
    expanded_boxes = []
    for box in boxes:
        x1, y1, x2, y2 = [int(coord) for coord in box]
        expansion_factor = 0.05  # Adjust the expansion factor as needed
        expand_x = int((x2 - x1) * expansion_factor)
        expand_y = int((y2 - y1) * expansion_factor)
        expanded_box = [max(0, x1 - expand_x), max(0, y1 - expand_y), min(image.shape[1], x2 + expand_x), min(image.shape[0], y2 + expand_y)]
        expanded_boxes.append(expanded_box)
    
    for expanded_box in expanded_boxes:
        x1, y1, x2, y2 = expanded_box
        cv2.rectangle(mask, (x1, y1), (x2, y2), (255, 255, 255), thickness=cv2.FILLED)
    
    # Invert the mask to keep everything except the detected objects
    mask_inv = cv2.bitwise_not(mask)
    
    # Apply the mask to the original image to hide objects
    result = cv2.bitwise_and(image, mask_inv)
    
    # Save the result and override the original image
    cv2.imwrite(image_path, result)


# if __name__ == "__main__":
#     # Load the pre-trained model with the most up-to-date weights
#     model = load_model(weights="SSD300_VGG16_Weights.DEFAULT")
    
#     # Path to the input image
#     image_path = "x.jpg"
    
#     # Detect objects in the image
#     object_boxes = detect_objects(model, image_path)
    

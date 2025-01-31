import os

image_dir = "dataset/images"
train_file = "dataset/train.txt"
valid_file = "dataset/valid.txt"

# List all images
images = [os.path.join(image_dir, img) for img in os.listdir(image_dir) if img.endswith(('.jpg', '.png'))]

# Split into train and validation sets (e.g., 80% train, 20% validation)
split = int(0.8 * len(images))
train_images = images[:split]
valid_images = images[split:]

# Write to files
with open(train_file, "w") as f:
    f.write("\n".join(train_images))

with open(valid_file, "w") as f:
    f.write("\n".join(valid_images))
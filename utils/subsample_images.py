import os
import shutil

def copy_image_each_n(src_dir, dst_dir, n):
    """
    Copy 1 out of every n .jpg images from 'src_dir' to 'dst_dir'.

    Parameters:
        src_dir (str): Path to the directory with the original images.
        dst_dir (str): Path to the directory where selected images will be copied.
        n (int): Interval for copying (e.g., n=10 copies 1 out of every 10 images).
    """

    # Create destination directory if it does not exist
    os.makedirs(dst_dir, exist_ok=True)

    # List and sort all .jpg images by filename (timestamps)
    images = sorted([f for f in os.listdir(src_dir) if f.endswith(".jpg")])

    # Loop through images and copy 1 out of every n
    for i, img in enumerate(images):
        if i % n == 0:  # take every n-th image
            src_path = os.path.join(src_dir, img)
            dst_path = os.path.join(dst_dir, img)
            shutil.copy2(src_path, dst_path)  # preserve metadata
            print(f"Copied: {img}")


# Main execution block
if __name__ == "__main__":
    
    src_dir = "/home/miguelangel/oxford-lab/labrobotics/nerf-logs/2025-08-14-wytham/sapling-04/raw/images/cam1-full"
    dst_dir = "/home/miguelangel/oxford-lab/labrobotics/nerf-logs/2025-08-14-wytham/sapling-04/raw/images/cam1"
    n = 3
    
    copy_image_each_n(src_dir, dst_dir, n)
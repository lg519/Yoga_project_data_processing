from collections import defaultdict
from tkinter import filedialog, Tk
from scipy.io import loadmat
import os
import numpy as np
import matplotlib.pyplot as plt

from apply_processing_pipeline import normalize_signal
from amplifier_config import sampling_frequency
from utilis import get_mat_filenames, get_partecipant_type, get_exercise_name
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
from PIL import Image, ImageDraw, ImageFont


def plot_heatmap(activations, active_channels, title, save_path):
    grid = np.zeros((8, 8))
    for i, ch in enumerate(active_channels):
        row = (ch - 1) // 8
        col = (ch - 1) % 8
        grid[row][col] = activations[i]
    plt.imshow(grid, cmap="viridis", interpolation="nearest")
    for i, ch in enumerate(active_channels):
        row = (ch - 1) // 8
        col = (ch - 1) % 8
        plt.text(
            col,
            row,
            str(ch),
            ha="center",
            va="center",
            color="white" if activations[i] < 0.5 else "black",
        )
    plt.colorbar(label="Muscle Activation")
    plt.title(title)
    plt.axis("off")
    plt.savefig(save_path, dpi=300, bbox_inches="tight")
    plt.close()


from matplotlib.transforms import Affine2D

from matplotlib.cm import get_cmap


def plot_combined_heatmap_on_bg(
    activations_list,
    active_channels_list,
    title,
    save_path,
    background_path,
    positions,
    scales,
    rotations,
):
    fig, ax = plt.subplots(figsize=(15, 5))
    bg_img = plt.imread(background_path)
    ax.imshow(bg_img, aspect="equal", extent=[0, bg_img.shape[1], 0, bg_img.shape[0]])

    # Define a colormap to pick colors for arrows
    colormap = get_cmap(
        "tab10"
    )  # Using 'tab10' which has 10 distinguishable colors, but you can choose any other
    arrow_colors = [colormap(i) for i in range(len(activations_list))]

    arrow_artists = []  # This list will be used to create the legend

    for idx, (activations, active_channels, pos, scale, rotation) in enumerate(
        zip(activations_list, active_channels_list, positions, scales, rotations)
    ):
        grid = np.zeros((8, 8))
        for i, ch in enumerate(active_channels):
            row = (ch - 1) // 8
            col = (ch - 1) % 8
            grid[row][col] = activations[i]

        # Convert grid to RGB image using viridis colormap
        grid_colored = plt.cm.viridis(grid / np.max(grid))
        grid_rgb = (grid_colored[:, :, :3] * 255).astype(np.uint8)

        # Create Affine transformation for grid
        rot_trans = (
            Affine2D()
            .translate(-pos[0], -pos[1])
            .rotate_deg(rotation)
            .translate(pos[0], pos[1])
        )
        ax.imshow(
            grid_rgb,
            extent=[
                pos[0],
                pos[0] + grid_rgb.shape[1] * scale,
                pos[1],
                pos[1] + grid_rgb.shape[0] * scale,
            ],
            transform=rot_trans + ax.transData,
            interpolation="nearest",
        )

        # Adjust arrow position based on rotation
        arrow_x = pos[0] + grid_rgb.shape[1] * scale  # Exactly on the right border
        arrow_y = pos[1] + grid_rgb.shape[0] * scale / 2  # Centered vertically
        arrow_x, arrow_y = rot_trans.transform_point([arrow_x, arrow_y])
        arrow_artist = ax.arrow(
            arrow_x,
            arrow_y,
            10 * np.cos(np.radians(rotation)),
            10 * np.sin(np.radians(rotation)),
            head_width=5,
            head_length=10,
            fc=arrow_colors[idx],
            ec=arrow_colors[idx],
            label=f"Grid {idx + 1}",  # We add label to arrow for the legend
        )
        arrow_artists.append(arrow_artist)

    ax.set_title(title, fontsize=10, y=1.15)
    ax.legend(
        handles=arrow_artists, loc="upper right"
    )  # Displaying legend using arrow artists
    ax.axis("off")
    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches="tight")
    plt.close()


def compute_exercise_activations(filenames, channel_indices, mvc_values):
    activations_per_exercise = defaultdict(lambda: [list() for _ in channel_indices])

    for filename in filenames:
        mat_file = loadmat(filename)
        data = mat_file["data"]
        exercise_name = get_exercise_name(os.path.basename(filename))

        for channel_index in channel_indices:
            processed_data = normalize_signal(
                data[channel_index, :],
                sampling_frequency,
                mvc_values[channel_index],
            )
            activations_per_exercise[exercise_name][channel_index].append(
                processed_data
            )

    return activations_per_exercise


if __name__ == "__main__":
    root = Tk()
    root.withdraw()

    directory_path = filedialog.askdirectory(
        title="Select directory with exercise data"
    )

    mvc_values = [1] * 64  # Assigning all 64 values to 1

    filenames = get_mat_filenames(directory_path)
    participant_type = get_partecipant_type(filenames[0])

    activations_per_exercise = compute_exercise_activations(
        filenames, range(64), mvc_values  # Assuming 64 channels in total
    )

    grids = [
        (
            1,
            [
                1,
                3,
                5,
                7,
                12,
                14,
                17,
                19,
                21,
                23,
                26,
                33,
                35,
                37,
                39,
                44,
                46,
                49,
                51,
                53,
                55,
                60,
            ],
        ),
        (
            2,
            [
                1,
                3,
                5,
                7,
                12,
                14,
                17,
                19,
                21,
                23,
                33,
                35,
                37,
                39,
                44,
                46,
                49,
                51,
                53,
                55,
                60,
            ],
        ),
        (
            3,
            [
                1,
                3,
                5,
                7,
                12,
                14,
                17,
                19,
                21,
                23,
                33,
                35,
                37,
                39,
                44,
                46,
                49,
                51,
                53,
                55,
                60,
            ],
        ),
    ]

    save_directory = os.path.join(directory_path, "figures_heatmaps")
    os.makedirs(save_directory, exist_ok=True)

    for exercise_name, all_activations in activations_per_exercise.items():
        for rep_index in range(len(all_activations[0])):
            combined_activations = [
                [
                    np.mean(all_activations[i][rep_index])
                    for i in range(
                        sum(len(grid[1]) for grid in grids[:index]),
                        sum(len(grid[1]) for grid in grids[: index + 1]),
                    )
                ]
                for index, (grid_num, active_channels) in enumerate(grids)
            ]
            heatmap_save_path = os.path.join(
                save_directory,
                f"{participant_type} - Combined Grids - {exercise_name} - Rep {rep_index + 1} - Heatmap.png",
            )
            positions = [(100, 200), (300, 200), (500, 200)]  # adjust these as required
            background_path = "Process_EMG_data/images/Human_Body_Diagram.jpg"
            scales = [4, 4, 4]  # adjust these scales as required
            rotations = [0, 45, 90]

            plot_combined_heatmap_on_bg(
                combined_activations,
                [grid[1] for grid in grids],
                f"{participant_type} - Combined Grids - {exercise_name} - Rep {rep_index + 1}",
                heatmap_save_path,
                background_path,
                positions,
                scales,
                rotations,
            )

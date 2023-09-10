from collections import defaultdict
from tkinter import filedialog, Tk
from scipy.io import loadmat
import os
import numpy as np
import matplotlib.pyplot as plt

from apply_processing_pipeline import normalize_signal
from amplifier_config import sampling_frequency
from utilis import get_mat_filenames, get_partecipant_type, get_exercise_name


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


def plot_combined_heatmap(activations_list, active_channels_list, title, save_path):
    fig, axes = plt.subplots(1, len(activations_list), figsize=(15, 5))

    for idx, (ax, activations, active_channels) in enumerate(
        zip(axes, activations_list, active_channels_list)
    ):
        grid = np.zeros((8, 8))
        for i, ch in enumerate(active_channels):
            row = (ch - 1) // 8
            col = (ch - 1) % 8
            grid[row][col] = activations[i]
        ax.imshow(grid, cmap="viridis", interpolation="nearest")
        for i, ch in enumerate(active_channels):
            row = (ch - 1) // 8
            col = (ch - 1) % 8
            ax.text(
                col,
                row,
                str(ch),
                ha="center",
                va="center",
                color="white" if activations[i] < 0.5 else "black",
            )
        ax.set_title(f"Grid {idx + 1}")  # Updated line
        ax.axis("off")

    plt.colorbar(ax.images[0], ax=axes, label="Muscle Activation", location="right")
    plt.suptitle(title)
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
            plot_combined_heatmap(
                combined_activations,
                [grid[1] for grid in grids],
                f"{participant_type} - Combined Grids - {exercise_name} - Rep {rep_index + 1}",
                heatmap_save_path,
            )

import numpy as np
from scipy.stats import pearsonr
import pandas as pd
import pingouin as pg
import os


def average_pearson_coefficient_over_directories(
    activations_by_directory, exercise_name
):
    """Calculate the average Pearson correlation between reps of the same exercise
    across directories based on their activations."""

    correlations = []

    # List of 8-dimensional vectors for each rep in every directory
    vectors_per_rep = []
    directory_rep_info = []  # Store directory and rep index for each vector

    # Loop over all directories (i.e., sessions or individuals)
    for (
        directory_path,
        channel_activations_by_directory,
    ) in activations_by_directory.items():
        # Number of reps (assuming all channels have the same number of reps)
        num_reps = len(channel_activations_by_directory[0])

        # Construct vectors for each rep in the current directory
        for rep_index in range(num_reps):
            vector_for_rep = [
                np.mean(channel_activations[rep_index]) if channel_activations else 0
                for channel_activations in channel_activations_by_directory
            ]
            vectors_per_rep.append(vector_for_rep)
            directory_rep_info.append(
                (directory_path, rep_index)
            )  # Store the directory and rep info

    # Check and print vectors with NaN or inf values
    for i, vec in enumerate(vectors_per_rep):
        if np.any(np.isnan(vec)) or np.any(np.isinf(vec)):
            directory, rep_index = directory_rep_info[i]
            print(
                f"Exercise: {exercise_name}, Directory: {directory}, Rep: {rep_index + 1} has problematic values: {vec}"
            )

    # Compute correlations among vectors of reps
    for i in range(len(vectors_per_rep)):
        for j in range(i + 1, len(vectors_per_rep)):
            if len(vectors_per_rep[i]) == len(
                vectors_per_rep[j]
            ):  # Ensure the vectors have the same length
                # Check if either vector contains NaN or inf before correlation calculation
                if (
                    np.any(np.isnan(vectors_per_rep[i]))
                    or np.any(np.isnan(vectors_per_rep[j]))
                    or np.any(np.isinf(vectors_per_rep[i]))
                    or np.any(np.isinf(vectors_per_rep[j]))
                ):
                    print(
                        f"Pearson Coefficient: NaN or Infinity values found in vectors at indices {i} and/or {j}. Skipping these vectors."
                    )
                    continue
                correlation, _ = pearsonr(vectors_per_rep[i], vectors_per_rep[j])
                correlations.append(correlation)

    return np.mean(correlations)


def compute_icc_for_exercise(activations_by_directory, exercise_name):
    """Calculate the ICC across repetitions of the same exercise based on their activations."""
    data = []
    row_labels = []
    for (
        directory_path,
        channel_activations_by_directory,
    ) in activations_by_directory.items():
        # Number of reps (assuming all channels have the same number of reps)
        num_reps = len(channel_activations_by_directory[0])
        for rep_index in range(num_reps):
            vector_for_rep = [
                np.mean(channel_activations[rep_index]) if channel_activations else 0
                for channel_activations in channel_activations_by_directory
            ]
            data.append(vector_for_rep)
            row_labels.append(
                f"{os.path.basename(directory_path).split('_')[0]}_Rep{rep_index+1}"
            )

    # Naming the columns
    num_channels = len(data[0])
    column_names = [f"Channel_{i+1}" for i in range(num_channels)]

    df = pd.DataFrame(data, columns=column_names, index=row_labels)
    # Reshaping the dataframe
    df_melted = df.melt(
        ignore_index=False, var_name="target", value_name="rating"
    ).reset_index()
    df_melted.columns = ["rater", "target", "rating"]
    # print(f"Melted dataframe for exercise {exercise_name}")
    # print(df_melted)

    # Compute the ICC
    icc_results = pg.intraclass_corr(
        data=df_melted, targets="target", raters="rater", ratings="rating"
    ).round(3)
    # print(f"\nICC results for exercise {exercise_name}:")
    # print(icc_results)

    # Extract ICC2 value from the results
    icc2_value = icc_results.loc[icc_results["Type"] == "ICC2", "ICC"].values[0]
    return icc2_value


def cosine_similarity(v1, v2):
    """Compute the cosine similarity between two vectors."""
    dot_product = np.dot(v1, v2)
    norm_v1 = np.linalg.norm(v1)
    norm_v2 = np.linalg.norm(v2)

    if norm_v1 == 0 or norm_v2 == 0:
        # One of the vectors is a zero-vector, which will cause division by zero.
        return 0.0

    return dot_product / (norm_v1 * norm_v2)


def average_cosine_similarity_over_directories(activations_by_directory, exercise_name):
    """Calculate the average cosine similarity between reps of the same exercise
    across directories based on their activations."""

    similarities = []

    # List of 8-dimensional vectors for each rep in every directory
    vectors_per_rep = []
    directory_rep_info = []  # Store directory and rep index for each vector

    # Loop over all directories (i.e., sessions or individuals)
    for (
        directory_path,
        channel_activations_by_directory,
    ) in activations_by_directory.items():
        # Number of reps (assuming all channels have the same number of reps)
        num_reps = len(channel_activations_by_directory[0])

        # Construct vectors for each rep in the current directory
        for rep_index in range(num_reps):
            vector_for_rep = [
                np.mean(channel_activations[rep_index]) if channel_activations else 0
                for channel_activations in channel_activations_by_directory
            ]
            vectors_per_rep.append(vector_for_rep)
            directory_rep_info.append(
                (directory_path, rep_index)
            )  # Store the directory and rep info

    # Check and print vectors with NaN or inf values
    for i, vec in enumerate(vectors_per_rep):
        if np.any(np.isnan(vec)) or np.any(np.isinf(vec)):
            directory, rep_index = directory_rep_info[i]
            print(
                f"Exercise: {exercise_name}, Directory: {directory}, Rep: {rep_index + 1} has problematic values: {vec}"
            )

    # Compute cosine similarities among vectors of reps
    for i in range(len(vectors_per_rep)):
        for j in range(i + 1, len(vectors_per_rep)):
            if len(vectors_per_rep[i]) == len(
                vectors_per_rep[j]
            ):  # Ensure the vectors have the same length
                if (
                    np.any(np.isnan(vectors_per_rep[i]))
                    or np.any(np.isnan(vectors_per_rep[j]))
                    or np.any(np.isinf(vectors_per_rep[i]))
                    or np.any(np.isinf(vectors_per_rep[j]))
                ):
                    print(
                        f"Cosine Similarity: NaN or Infinity values found in vectors at indices {i} and/or {j}. Skipping these vectors."
                    )
                    continue
                similarity = cosine_similarity(vectors_per_rep[i], vectors_per_rep[j])
                similarities.append(similarity)

    return np.mean(similarities)

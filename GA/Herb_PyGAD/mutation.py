import numpy as np


def custom_mutation(offspring, ga_instance):
    """
        2 random genes in the whoe parent array are selected and swapped.
        Then the parent array is returned with only 2 swapped values

        Complexity:
        O(1)

        Parameters:
        - offspring ([Int]): An Array of ints representing the id of the product. The offspring array is randomly selected by the GA

        Returns:
        An array where 2 genes have been swapped
    """
    for chromosome_idx in range(offspring.shape[0]):
        # Get 2 random indexes
        random_gene_idx_1 = np.random.choice(range(offspring.shape[1]))
        random_gene_idx_2 = np.random.choice(range(offspring.shape[1]))

        # Swap values
        # value = offspring[chromosome_idx, random_gene_idx_1]
        # offspring[chromosome_idx, random_gene_idx_1] = offspring[chromosome_idx, random_gene_idx_2]
        # offspring[chromosome_idx, random_gene_idx_2] = value
    return offspring
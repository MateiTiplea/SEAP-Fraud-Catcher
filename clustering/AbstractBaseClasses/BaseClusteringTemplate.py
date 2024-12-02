from abc import ABC, abstractmethod
from collections import defaultdict

import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics import silhouette_score, calinski_harabasz_score, davies_bouldin_score
import Levenshtein
from sklearn.metrics.pairwise import cosine_similarity
from clustering.MOP.ClusteringMeta import ClusteringMeta, monitor_function




class BaseClusteringTemplate(ABC,metaclass=ClusteringMeta):
    def __init__(self, list_of_items, clustering_strategy):
        self.list_of_items = list_of_items
        self.distance_matrix = self.get_distance_matrix(list_of_items)
        self.max_clusters = self.calculate_max_clusters()
        self.clustering_strategy = clustering_strategy

    def clean_invalid_items(self):
        """
        Elimină item-urile care nu respectă anumite reguli de validitate.
        """
        print("Executing CLEAN")
        valid_items = []
        for item in self.list_of_items:
            if item.name and item.closing_price > 0 and item.quantity > 0:
                valid_items.append(item)
            else:
                print(f"Invalid item removed: {item.name if item.name else 'Unnamed Item'}")
        self.list_of_items = valid_items


    def validate_items(self):
        """
        Validează dacă toate item-urile respectă structura așteptată.
        """
        print("Executing VALIDATE")
        if not self.list_of_items:
            print("Validation failed: No items found!")
            return False

        for item in self.list_of_items:
            if not all([item.name, item.cpv_code_id, item.closing_price]):
                print(f"Validation failed: Missing fields in item {item.name if item.name else 'Unnamed Item'}")
                return False

        print("Validation successful")
        return True

    def execute_clustering(self):
        n_clusters = self.find_optimal_clusters()
        return self.perform_clustering(n_clusters)

    def calculate_max_clusters(self):
        list_of_strings = [item.name.lower() for item in self.list_of_items]
        unique_strings = np.unique(list_of_strings)
        return min(len(unique_strings) - 1, len(self.list_of_items) - 1)

    def processes_strings(self, str1, str2):

        if str1.startswith(str2):
            return str2, str2
        elif str2.startswith(str1):
            return str1, str1

        words1 = str1.split()
        words2 = str2.split()

        new_str1 = ""
        new_str2 = ""

        i = 0
        while i < len(words1) and i < len(words2):
            word1 = words1[i]
            word2 = words2[i]

            if word1.startswith(word2) or word2.startswith(word1):
                if new_str1:
                    new_str1 += " "
                new_str1 += word2

                if new_str2:
                    new_str2 += " "
                new_str2 += word2
            else:
                if new_str1:
                    new_str1 += " "
                new_str1 += word1

                if new_str2:
                    new_str2 += " "
                new_str2 += word2

            i += 1

        return new_str1, new_str2

    def jaccard_similarity(self, string1, string2):
        words1 = set(string1.split())
        words2 = set(string2.split())
        intersection = words1 & words2
        if len(intersection) == len(words1) or len(intersection) == len(words2):
            return 1
        union = words1 | words2
        return len(intersection) / len(union)

    def get_distance_matrix(self, items):
        n = len(items)
        distance_matrix = np.zeros((n, n))
        for i in range(n):
            for j in range(i + 1, n):
                str1_to_cmp, str2_to_cmp = self.processes_strings(items[i].name.lower(), items[j].name.lower())
                dist = Levenshtein.distance(str1_to_cmp, str2_to_cmp)

                distance_matrix[i, j] = dist
                distance_matrix[j, i] = dist
        return distance_matrix

    def find_optimal_clusters(self, metric="calinski_harabasz"):
        scores = []
        for n_clusters in range(2, self.max_clusters + 1):
            cluster_labels = self.clustering_strategy.cluster(self.distance_matrix, n_clusters)

            if metric == "silhouette":
                score = silhouette_score(self.distance_matrix, cluster_labels, metric="precomputed")

            elif metric == "calinski_harabasz":
                score = calinski_harabasz_score(self.distance_matrix, cluster_labels)

            else:
                raise ValueError(
                    f"Metric {metric} not supported. Choose from 'silhouette', 'calinski_harabasz', or 'davies_bouldin'.")

            scores.append((n_clusters, score))

        if not scores:
            return None

        return max(scores, key=lambda x: x[1])[0]

    def dynamic_filter_by_model(self):
        """
        Grupează dinamic elementele pe baza similarității denumirilor lor.
        """
        item_names = [item.name.lower() for item in self.list_of_items]

        # Vectorizare text pentru similaritate
        vectorizer = CountVectorizer().fit_transform(item_names)
        vectors = vectorizer.toarray()

        # Calculăm similaritatea cosinus
        similarity_matrix = cosine_similarity(vectors)

        # Grupare bazată pe similaritate
        threshold = 0.5  # Pragul pentru considerarea unui element ca similar
        model_groups = defaultdict(list)
        visited = set()

        for i, item in enumerate(self.list_of_items):
            if i in visited:
                continue

            group = [item]
            visited.add(i)

            for j, other_item in enumerate(self.list_of_items):
                if j != i and j not in visited:
                    if similarity_matrix[i, j] >= threshold:
                        group.append(other_item)
                        visited.add(j)

            model_name = self.extract_common_words([x.name for x in group])
            model_groups[model_name].extend(group)

        return model_groups

    @staticmethod
    def extract_common_words(names):
        """
        Extrage cuvintele comune dintr-o listă de denumiri.
        """
        word_sets = [set(name.split()) for name in names]
        common_words = set.intersection(*word_sets) if word_sets else set()
        return " ".join(common_words) if common_words else "Generic"


    @abstractmethod
    def perform_clustering(self, n_clusters):

        pass

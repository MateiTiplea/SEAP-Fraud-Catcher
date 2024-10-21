from clustering_algorithm import get_clusters
from database.db_config import MongoDBClient
from database.operations import MongoOperations
import configparser
import random
import Levenshtein

def generate_random_transactions(n):
    categories = ["Apple", "Samsung", "Huawei", "Dell", "HP", "Lenovo", "Microsoft", "Nokia", "Xiaomi", "LG"]
    products = ["laptop", "telefon", "tabletă", "monitor", "tastatură", "imprimantă", "mouse", "smartwatch", "server", "căști"]

    transactions = []
    for _ in range(n):
        category = random.choice(categories)
        product = random.choice(products)
        action = random.choice(["Cumpărare", "Achiziție", "Contract de furnizare pentru", "Licitație pentru"])
        price = random.randint(100, 5000)  # preț fictiv
        transaction_title = f"{action} {product} {category} - preț: {price} RON"
        transactions.append(transaction_title)
    return transactions

def write_transactions_to_file(filename, transactions):
    with open(filename, "w", encoding="utf-8") as f:
        for transaction in transactions:
            f.write(transaction + "\n")

def read_transactions_from_file(filename):
    with open(filename, "r", encoding="utf-8") as f:
        transactions = [line.strip() for line in f.readlines()]
    return transactions

def find_transactions_with_keyword(keyword, cluster_dict, max_distance=3):
    keyword_lower = keyword.lower()
    found_transactions = []

    for cluster, titles in cluster_dict.items():
        for title in titles:
            title_lower = title.lower()
            words = title_lower.split()
            for word in words:
                distance = Levenshtein.distance(keyword_lower, word)
                if distance <= max_distance:
                    found_transactions.append((cluster, title))
                    break
    return found_transactions


def main():
    # Testare conexiune cu baza de date
    config = configparser.ConfigParser()
    config.read('db_config.properties')

    MONGO_URI = config.get('MongoDB', 'mongodb.uri')
    DATABASE_NAME = config.get('MongoDB', 'mongodb.name')

    mongo_client = MongoDBClient(uri=MONGO_URI, database=DATABASE_NAME)
    mongo_client.connect()

    db = mongo_client.get_database()

    mongo_ops = MongoOperations(db)
    tests = mongo_ops.find('test')

    for test_ in tests:
        print(test_)

    mongo_client.close()

    transactions_file = "transactions.txt"
    try:
        transactions = read_transactions_from_file(transactions_file)
        print(f"{len(transactions)} tranzacții citite din '{transactions_file}'.")
    except FileNotFoundError:
        transactions = generate_random_transactions(500)
        write_transactions_to_file(transactions_file, transactions)
        print(f"{len(transactions)} tranzacții generate și salvate în '{transactions_file}'.")

    cluster_dict = get_clusters(transactions)

    with open("clustered_transactions.txt", "w", encoding="utf-8") as f:
        for cluster, titles in cluster_dict.items():
            f.write(f"Cluster {cluster}:\n")
            for title in titles:
                f.write(f" - {title}\n")
            f.write("\n")
    print("Clusterizarea a fost salvată în clustered_transactions.txt.")

    keyword = input("Introduceți un keyword pentru a găsi tranzacțiile relevante: ")

    found_transactions = find_transactions_with_keyword(keyword, cluster_dict)

    if found_transactions:
        print(f"\nTranzacții similare cu '{keyword}':\n")
        for cluster, title in found_transactions:
            print(f"Cluster {cluster}: {title}")
    else:
        print(f"Nu au fost găsite tranzacții care să fie similare cu keyword-ul '{keyword}'.")


if __name__ == "__main__":
    main()

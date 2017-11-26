import os
import sys
from MatifyAPI import MatifyAPI
from requests import Session
import io
import json
import csv

DATASET_DIR = 'Datasets/'

matifyAPI = MatifyAPI(verbose=False)
categories = matifyAPI.getCategories()
#Request products from all sub category
allProducts = []
for categoryId, categoryName, subCategories in categories:
    #products = matifyAPI.getProducts (categoryId, categoryName)
    #allProducts.append([categoryName, products])
    for subCategoryID, subCategoryName, _ in subCategories:
        try:
            supermarkets = matifyAPI.getProducts (subCategoryID, subCategoryName)
            print(subCategoryName)
            for supermarket in supermarkets:
                allProducts.append([subCategoryID, subCategoryName, supermarket["products"]])
        except Exception as e:
            print(e)
            continue
            
with open(os.path.join(DATASET_DIR, 'train.csv'), 'wb') as csvfile:
    csvwriter = csv.writer(csvfile, delimiter=';',
                           quotechar='|', quoting=csv.QUOTE_MINIMAL)
    csvwriter.writerow(['category_id', 'category', 'image', 'name', 'description'])
    for categoryId, categoryName, products in allProducts:
        categoryPath =  os.path.join(DATASET_DIR,
                                     categoryName)
        for product in products:
            if product["image"]:
                try:
                    image_path = os.path.join(categoryPath, str(product["id"]) + ".jpg")
                    csvwriter.writerow([categoryId,
                                        categoryName.encode('utf-8'),
                                        image_path.encode('utf-8'), 
                                        product["name"].encode('utf-8'), 
                                        product["description"].encode('utf-8')])
                    csvfile.flush()
                except Exception as e:
                    print (e)
                    continue


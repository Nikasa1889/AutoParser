from requests import Session
from tabulate import tabulate
import json
SERVER_ADDR = 'http://52.59.243.6:8000/'

def getCategories (session, verbose = True):
    categoryResponse = session.get(SERVER_ADDR + 'listCategories/', headers={'Accept':'application/json'})
    categories = json.loads(categoryResponse.text)
    categoryList = [[category['id'], category['name'], 
                     [[subCategory['id'], subCategory['name'], subCategory['numOfProducts']] 
                      for subCategory in category['sub_categories']]] 
                    for category in categories]
    if verbose:
        for categoryId, categoryName, subCategories in categoryList:
            print "----------------------------------------"
            print categoryName + " (ID: " + str(categoryId) +")"
            print tabulate(subCategories, headers=["Sub Id", "Name", "Num of Products"])
    return categoryList

def getProducts (session, categoryId, categoryName = '', expired_after = '2015-01-01', verbose = True):
    productsResponse = session.get(SERVER_ADDR + 'listProducts/?categoryId='+
                                   str(categoryId)+'&offset=0&len=200'+
                                   '&expired_after='+expired_after, 
                                   headers={'Accept':'application/json'})
    products = json.loads(productsResponse.text)
    if verbose:
        print categoryName + "(ID=" + str(categoryId) + ")" + ": " + str(len(products))
        print products
    return products

def filterProductWithImage (allProducts, verbose = True):
    productWithImages = []
    for categoryName, products in allProducts:
        filteredProducts = [product for product in products if product["image"]]
        productWithImages.append([categoryName, filteredProducts])
        print  '%22s : %d images' %(categoryName, len(filteredProducts))
    return productWithImages
    
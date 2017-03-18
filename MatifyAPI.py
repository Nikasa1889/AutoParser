from requests import Session
from tabulate import tabulate
import json
SERVER_API_ENDPOINT = 'http://52.59.243.6:8000/'

class MatifyAPI:
    def __init__(self, verbose = True):
        self.verbose = verbose
        self.session = Session()
        self.defaultHeaders = {'Accept':'application/json'}
        
    def getCategories (self):
        categoryResponse = self.session.get(SERVER_API_ENDPOINT + 'listCategories/', 
                                       headers=self.defaultHeaders)
        assert (int(categoryResponse.status_code) == 200), \
                "Error when requesting all categories. Response text: " + categoryResponse.text

        categories = json.loads(categoryResponse.text)
        categoryList = [[category['id'], category['name'], 
                         [[subCategory['id'], subCategory['name'], subCategory['numOfProducts']] 
                          for subCategory in category['sub_categories']]] 
                        for category in categories]
        if self.verbose:
            for categoryId, categoryName, subCategories in categoryList:
                print "----------------------------------------"
                print categoryName + " (ID: " + str(categoryId) +")"
                print tabulate(subCategories, headers=["Sub Id", "Name", "Num of Products"])
        return categoryList

    def getProducts (self, categoryId, categoryName = '', expired_after = '2015-01-01'):
        productsResponse = self.session.get(SERVER_API_ENDPOINT + 'listProducts/?categoryId='+
                                           str(categoryId)+'&offset=0&len=200'+
                                           '&expired_after='+expired_after, 
                                           headers=self.defaultHeaders)
        assert (int(productsResponse.status_code) == 200), \
                "Error when requesting all products of a catagory. Response text: " + productsResponse.text

        products = json.loads(productsResponse.text)
        if self.verbose:
            print categoryName + "(ID=" + str(categoryId) + ")" + ": " + str(len(products))
            print products
        return products

    def filterProductWithImage (self, allProducts):
        productWithImages = []
        for categoryName, products in allProducts:
            filteredProducts = [product for product in products if product["image"]]
            productWithImages.append([categoryName, filteredProducts])
            if self.verbose:
                print  '%22s : %d images' %(categoryName, len(filteredProducts))
        return productWithImages

    def uploadCatalog (self, catalogJson, catalogId, catalogName):
        token = 'b2h6ylyfn6pfvoz5wuvc'
        if self.verbose:
            print "Uploading catalog " + catalogName 

        response = self.session.post( SERVER_API_ENDPOINT + 'upload_products/'+str(catalogId),
                                  data = {"token":token, 
                                          "file_name":catalogName, 
                                          "data": catalogJson})
        assert (int(response.status_code) == 200), \
                "Error when uploading catalog. Response text: " + response.text

        if self.verbose:
            print response
            print response.text
        return response
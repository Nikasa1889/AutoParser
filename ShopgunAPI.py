from requests import Session
from tabulate import tabulate
import json
import io
SERVER_API_ENDPOINT = 'https://api.etilbudsavis.dk/v2/'
MATIFY_API_KEY = '00izwus560vpbdasf0o92m2fhaim4ynr'
SELECTED_BRAND_NAME = ['coop mega', 'coop extra', 'coop marked', 'kiwi', 'meny', 'rema', 'matkroken', \
                       'coop prix','joker', 'bunnpris', 'extra', 'spar']
class ShopgunAPI:
    '''
        
    '''
    def __init__(self, verbose = True):
        '''
            Create a session, ask for token, and use that for all subsequent requests
        '''
        self.session = Session()
        self.verbose = verbose
        self.token   = self.getToken()
        self.defaultHeaders = {'X-token': self.token, 'Origin': "https://etilbudsavis.dk/"}
        
    def getToken(self):
        tokenResponse = self.session.post(SERVER_API_ENDPOINT + 'sessions?api_key=' + MATIFY_API_KEY)
        assert (int(tokenResponse.status_code) == 201), \
                "Error when requesting token. Response text: " + tokenResponse.text
        
        token = (json.loads(tokenResponse.text))["token"]
        if not token:
            raise  Exception("Couldn't get token")
        return token
    
    def getStores(self, limit=100):
        #List Store. 
        listResponse = self.session.get(SERVER_API_ENDPOINT + 
                                        'stores?r_lat=59.95&r_lng=10.75&r_radius=700000&api_av=0.1.33'+
                                        '&limit=' + str(limit),
                                        headers=self.defaultHeaders)
        assert (int(listResponse.status_code) == 200), \
                "Error when requesting all stores. Response text: " + listResponse.text
        
        stores = json.loads(listResponse.text)
        storeList = [[store['branding']['name'], store['id']] for store in stores]
        if self.verbose:
            print "-----------------List 100 stores-----------------------------"
            print tabulate(storeList, headers=['All Stores', 'Id'])
        return storeList
    
    def getCatalogs(self, selectedBrandNames = SELECTED_BRAND_NAME):
        catalogsResponse = self.session.get(SERVER_API_ENDPOINT + 
                                           'catalogs?r_lat=59.95'+
                                           '&r_lng=10.75&r_radius=700000&api_av=0.1.33&limit=100',
                                            headers=self.defaultHeaders)
        assert (int(catalogsResponse.status_code) == 200), \
                "Error when requesting all catalogs. Response text: " + catalogsResponse.text
        
        catalogs = json.loads(catalogsResponse.text)
        catalogList = [[catalog['branding']['name'], catalog['store_id'], catalog['id']] for catalog in catalogs]
        if self.verbose:
            print tabulate(catalogList, headers=['All Catalogs', 'Store Id', 'Id'])
        #If selectedBrandNames == None then return all catalogs
        if not selectedBrandNames:
            return catalogList
        #Check if any the brand name contains any selectedBrandName
        selectedCatalogs = [catalog for catalog in catalogs 
                            if len([brandName for brandName in selectedBrandNames 
                                    if brandName in catalog['branding']['name'].lower()]) > 0]
        selectedCatalogList = [[catalog['branding']['name'], catalog['id'], catalog['run_from'], 
                                next(brandName for brandName in selectedBrandNames 
                                     if brandName in catalog['branding']['name'].lower())] 
                               for catalog in selectedCatalogs]
        if self.verbose:
            print "\n---------------------------------"
            print tabulate(selectedCatalogList, headers=['Selected Catalogs', 'Id', 'Run From', 'Brand'])
        return selectedCatalogList
    
    def getOfferIdsOfCatalog(self, catalogId, catalogName = ''):
        if self.verbose:
            print "--------------------------------------------"
            print "Requesting catalog "+catalogName+" with id "+catalogId+"..."
            
        offersResponse = self.session.get(SERVER_API_ENDPOINT + 'catalogs/'+catalogId+
                                          '/hotspots?r_lat=59.95&r_lng=10.75&r_radius=700000&api_av=0.1.33',
                                           headers=self.defaultHeaders)
        assert (int(offersResponse.status_code) == 200), \
                "Error when requesting catalog. Response text: " + offersResponse.text
        
        offers = json.loads(offersResponse.text)
        if self.verbose:
            print "Number of offers: "+ str(len(offers))
        offerIdList = [offer['id'] for offer in offers]
        return offerIdList
        
    def getOfferDescription(self, offerId):
        offerDescResponse = self.session.get(SERVER_API_ENDPOINT + 'offers/'+offerId+
                                            '?r_lat=59.95&r_lng=10.75&r_radius=700000&api_av=0.1.33',
                                            headers=self.defaultHeaders)
        assert (int(offerDescResponse.status_code) == 200), \
                "Error when requesting offer description. Response text: " + offerDescResponse.text
        
        return json.loads(offerDescResponse.text.encode('utf-8'))
    
    def getOfferDescriptionsOfCatalog(self, catalogId, catalogName = ''):
        offerIdList = self.getOfferIdsOfCatalog(catalogId, catalogName);
        offerDescList = []
        for offerId in offerIdList:
            offerDesc = self.getOfferDescription(offerId);
            offerDescList.append(offerDesc)
        return offerDescList
    
    def generateCatalogFileName(self, catalogBrand, catalogId, catalogRunFrom):
        return catalogBrand + '_'+catalogId + "_" + catalogRunFrom + ".json"
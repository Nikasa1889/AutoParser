from ShopgunAPI import ShopgunAPI
import json
import io

shopgunAPI = ShopgunAPI(verbose=True);

selectedBrandNames = ['coop mega', 'coop extra', 'coop marked', \
                      'kiwi', 'meny', 'rema', 'matkroken',\
                      'coop prix','joker', 'bunnpris', 'extra', 'spar']
#selectedBrandNames = ['coop mega']
selectedCatalogList = shopgunAPI.getCatalogs(selectedBrandNames=selectedBrandNames)

from MatifyAPI import MatifyAPI
matifyAPI = MatifyAPI()
#Get offers in selected catalogs
for catalogStore, catalogId, catalogRunFrom, catalogBrand in selectedCatalogList:
    offerDescList = shopgunAPI.getOfferDescriptionsOfCatalog(catalogId, catalogStore)
    JsonFileName = shopgunAPI.generateCatalogFileName(catalogBrand, catalogId, catalogRunFrom)
    data = json.dumps(list(offerDescList), ensure_ascii=False)     
    #json_file.write(unicode(data))
    matifyAPI.uploadCatalog(brandName=catalogBrand, catalogData=data, catalogFileName=JsonFileName)
    print("Done.")



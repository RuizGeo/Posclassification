o# -*- coding: utf-8 -*-
"""
Created on Fri Apr  8 15:07:03 2016

@author: ruiz
"""
import numpy as np
import gdal
from statsmodels.stats import inter_rater
import geopandas as gp
from sklearn import tree
from sklearn.ensemble import RandomForestClassifier
import rasters_to_hdf5 as hdf
import h5py

def writeGeoIMG(path_img, path_out_img,outArray):
    #Read image
    img = gdal.Open(path_img, gdal.GA_ReadOnly)
    #Obtendo o drive para criar a imagem, que sera igual a da imagem aberta
    driver = img.GetDriver()
    #Criando a imagem no HD
    outDataset = driver.Create(path_out_img, img.RasterXSize, img.RasterYSize, 1, gdal.GDT_UInt32)
    #Get geoTransform
    geotransform = img.GetGeoTransform()
    #Obtendo a banda da imagem para poder gravar nela e
    outBand = outDataset.GetRasterBand(1)
    #inserir nodata
    outBand.SetNoDataValue(-99999)
    #Escrevendo na banda o cálculo
    outBand.WriteArray(outArray)
    #Georreferenciando a imagem criada, obtendo as coordenadas do canto
    outDataset.SetGeoTransform(geotransform)
    #Obtendo o sistema de coordeanada da imagem aberta e passando para a nova
    proj = img.GetProjection()
    #Set projection
    outDataset.SetProjection(proj)
    del outDataset
    return  
#Obterhapefiles treinamento e validacao
f_classificacao='//home/ruiz/Documentos/Pesquisas/Pos_classificacao/SVM.tif'
f_trein='/media/ruiz/Documentos/Pesquisas/Cicatrizes_Eduardo/SHP/treinamento.shp'
f_validacao = '/media/ruiz/Documentos/Pesquisas/Cicatrizes_Eduardo/SHP/validacao.shp'
treinamento = gp.GeoDataFrame.from_file(f_trein)
class_trein = treinamento['CLASS'].values.astype(np.int)
#Remover colunas
treinamento = treinamento.drop('CLASS',1)
treinamento = treinamento.drop('geometry',1)
validacao = gp.GeoDataFrame.from_file(f_validacao)
class_valid = validacao['CLASS'].values.astype(np.int)
#Remover colunas
validacao = validacao.drop('CLASS',1)
validacao = validacao.drop('geometry',1)
#Criar array auxilares
cart = np.recarray((11,), dtype=[('kappa', np.float16), ('var', np.float16),('depht',np.int)])
randomForest= np.recarray((11,7), dtype=[('kappa', np.float16), ('var', np.float16),('depht',np.int),('estimators',np.int)])
#Classificacao CART
max_depth= [2,5]#[2,5,10,15,20,25,30,35,40,45,50]
'''for i,max_d in enumerate( max_depth):
    clf = tree.DecisionTreeClassifier( criterion= 'gini',max_depth = max_d)
    #Crate model classification tree
    modelTree = clf.fit(treinamento.values, class_trein)
    #aplicar classificacao
    classificacao=modelTree.predict(validacao)
    #calcular matriz confusao
    matrix_confusion=np.histogram2d(class_valid,classificacao,bins=(2,2))[0]
    #calcular kappa
    accuracy=inter_rater.cohens_kappa(matrix_confusion)
    print 'kappa: ',accuracy.kappa,' var: ',accuracy.var_kappa, ' depth: ',max_d
    cart['kappa'][i]=accuracy.kappa
    cart['var'][i]=accuracy.var_kappa
    cart['depht'][i]=max_d'''

#Classificacao Random Forest
n_estimator=[2,5]#,10,15,20,25,30]
for p,d in enumerate(max_depth):
    for j,n in enumerate(n_estimator):    
        RF = RandomForestClassifier(n_estimators=n,max_depth=d)
        modelRF = RF.fit(treinamento.values, class_trein)
        classificacao=modelRF.predict(validacao)
        matrix_confusion=np.histogram2d(class_valid,classificacao,bins=(2,2))[0]
        accuracy=inter_rater.cohens_kappa(matrix_confusion)
        print matrix_confusion
        print 'kappa: ',accuracy.kappa,' var: ',accuracy.var_kappa, ' depth - estimators: ',d,n
        randomForest[p][j]=(accuracy.kappa,accuracy.var_kappa ,d,n)
#Criar grafico com a AD
RF = RandomForestClassifier(n_estimators=10,max_depth=10)
modelRF = RF.fit(treinamento.values, class_trein)
classificacao=modelRF.predict(validacao)
#salvar grafico Random forest
tree.export_graphviz(modelRF.estimators_[-1].tree_, out_file='/media/ruiz/Documentos/Pesquisas/Cicatrizes_Eduardo/AD_RF_1_5.dot')
#Converter rasters para HDF5rasters_to_hdf5
#Pasta com os rasters
caminho='/media/ruiz/Documentos/Pesquisas/Cicatrizes_Eduardo/Raster'
arquivo_HDF5='/media/ruiz/Documentos/Pesquisas/Cicatrizes_Eduardo/dados12.hdf5'
#foramto dos rasters
formato = '.tif'    
#Obter nomes dos rasters
proc=hdf.Converter_rasters_to_HDF5(caminho, formato)
#obter os caminhos e os nomes dos rasters
proc.obterNomesRasters()
#converter raster pára hdf
f_hdf=proc.Converte_Rasters_to_HDF(arquivo_HDF5)
#Fechar e abrir para leitura
f_hdf.close()
#Leitura do HDF5
h5f = h5py.File(arquivo_HDF5,'r')
#criar raster array
arrayClassificacao=np.zeros((1211,995),dtype=np.int)

 #Classificar os dados   
classificacao=modelRF.predict(h5f['rasters'][:,:])
img='/media/ruiz/Documentos/Pesquisas/Cicatrizes_Eduardo/Raster/DECL.tif'
#escrever a classificacao
#writeGeoIMG(img,f_classificacao, classificacao.reshape(1211,995))


            

        
        


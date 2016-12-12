# -*- coding: utf-8 -*-
"""
Created on Sun Sep 18 19:42:14 2016

@author: ruiz
"""
import gdal
from skimage import measure
import numpy as np

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
    
def readIMG(f_classificacao):
    #Obter drives para todos os tipos de imagem
    gdal.AllRegister()
    #Get metadata image
    ds = gdal.Open(f_classificacao, gdal.GA_ReadOnly)
    #Get geoTransform
    geoTransform = ds.GetGeoTransform()
    print geoTransform
    #Obter a banda
    banda1=ds.GetRasterBand(1)
    #Obter Noda Value
    NoDataValue = banda1.GetNoDataValue()
    #Obter banda como array
    classificacao= banda1.ReadAsArray()
  
    return classificacao.astype(np.int32),NoDataValue
    
def GetLabelsNeighbors(regioes_props,classificacao,nodata):
    #Obter o total de classes
    classes = np.arange(7+1)
    print 'Classes: ',classes
    area=np.array([])
    #loop sobre todas as regioes
    for i, regprop in enumerate(regioes_props[10:]):   
        #avaliar areas menores que o limiar
        if regprop.area < 2000:
            print '###############################'
            #Inserir -99 nos valores iguais a zero e iguais ao maior valor da linha e coluna
            rows= np.where( np.asarray(regprop.coords[:,0]) == classificacao.shape[0]-1,-99,np.asarray(regprop.coords[:,0]))
            rows= np.where( rows == 0, -99,rows) 
            cols= np.where( np.asarray(regprop.coords[:,1]) == classificacao.shape[1]-1,-99,np.asarray(regprop.coords[:,1]))
            cols= np.where( cols == 0, -99,cols)
            indices=np.column_stack((rows,cols))
            #Deletar os pares de coordenadas que contem -99
            indices=np.delete(indices,np.where(indices==-99)[0],0)   
            print 'indices.shape: ', indices.shape
            #Obter coordenadas dos vizinhos
            uniqueValuesCoords =np.column_stack(([indices[:,0]-1,indices[:,1]-1]))
            uniqueValuesCoords =np.append(uniqueValuesCoords,np.column_stack(([indices[:,0]+1,indices[:,1]+1])),axis=0)
            uniqueValuesCoords =np.append(uniqueValuesCoords,np.column_stack(([indices[:,0]-1,indices[:,1]+1])),axis=0)
            uniqueValuesCoords =np.append(uniqueValuesCoords,np.column_stack(([indices[:,0]+1,indices[:,1]-1])),axis=0)
            #obter o numero de linhas e de colunas do array com as coordenadas   
            print 'uniqueValuesCoords.shape: ',uniqueValuesCoords.shape
            #Transformar array para recarray, possibilitando a exclusao de pares de coordenadas
            ncols = uniqueValuesCoords.shape[1]
            dtype= {'names':['{}'.format(n) for n in ['y','x']],'formats':ncols * [uniqueValuesCoords.dtype]}
            #Excluir coordenadas repetidas
            unique=np.unique(uniqueValuesCoords.view(dtype))
            #Classe da regiao
            classReg=classificacao[regprop.coords[0,0],regprop.coords[0,1]]
            print 'Classe da regiao: ',classReg
            #Classes dos vizinhos
            classNearest=np.unique(classificacao[unique['y'],unique['x']])
            print 'Classes vizinhos: ',classNearest
            #Verificar se ha os valores NoData e a classe da regiao
            boolNoDataClassReg = np.in1d(classNearest,[nodata,classReg])
            #Contar o total de valores NoData e da classe, como os dos viznhos
            countNearest = np.bincount(boolNoDataClassReg)
            print 'Count: ',countNearest
            #Evitar q nao tenha classe
            if countNearest.size>1:
                    
                #Selecionar regioes isoladas
                if countNearest[0] == 1:
                    area=np.append(area,regprop.area)
                    print 'Classe atribuida a regiao isolada: ',classNearest[np.in1d(boolNoDataClassReg, False)]
                    #Verificar a classe da regiao isolada
                    classAtribReg =classNearest[np.in1d(boolNoDataClassReg, False)][0]
                    #Criar excecao para classe pastagem resteva
                    if (classReg == 2 and classAtribReg == 1) or (classReg == 1 and classAtribReg == 2):
                        pass
                    
                    else:
                        #caso nao sejam as classes de exceccao ocorre normal                
                        classificacao[regprop.coords[:,0],regprop.coords[:,1]]=classAtribReg
                else:

                    #Classes dos vizinhos
                    countClassNearest = np.bincount(classificacao[unique['y'],unique['x']])
                    #Remover as classes q nao devem ser consideradas
                    if classReg==6: 
                        countClassNearest[6] = 0
                    print 'countClassNearest: ',countClassNearest
                    #Diminuir os pixels da regiao de analise
                    print 'countClassNearest[classReg]-regprop.area ',countClassNearest[classReg]-regprop.area
                    countClassNearest[classReg]=countClassNearest[classReg]-regprop.area
                    
                    #Inserir a classe com o maior numero de pixels
                    classificacao[regprop.coords[:,0],regprop.coords[:,1]]=classes[np.max(countClassNearest)==countClassNearest][0]
                    print 'classe atribuida: ',classes[np.max(countClassNearest)==countClassNearest][0]
            
            else:
                pass
            
            print 'i: ',i, ' Vizinhos: ',unique.shape, ' Area: ',regprop.area
            
        else:
            pass

    return classificacao,area
#criar amostras de
f_seg= '/home/ruiz/Documentos/Pesquisas/OBIA_KNN/Segmentacao/seg_10_100.tif'

#Output img
img_out='/home/ruiz/Documentos/Pesquisas/Pos_classificacao/pos500_context.tif'
#Classificacao
f_class='/home/ruiz/Documentos/Pesquisas/OBIA_KNN/k7_i7_la60_exp1.tif'
#Ler segmentacao
#segmentacao,nodatavalue=readIMG(f_seg)
#Ler classificacao
classificacao,nodatavalue=readIMG(f_class)
#Separar regioes em labels
regioes_labels=measure.label(classificacao)
#Obter props regioes
regioes_props=measure.regionprops(regioes_labels)
del(regioes_labels)
#Avaliar pixels isolados
classificacaoPos,area_iso=GetLabelsNeighbors(regioes_props,classificacao, nodatavalue)
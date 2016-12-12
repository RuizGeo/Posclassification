# -*- coding: utf-8 -*-
"""
Created on Mon Apr 11 11:28:34 2016

@author: ruiz
"""
import gdal
import numpy as np
import os
import h5py


class Converter_rasters_to_HDF5:
    '''
    #Pasta com os rasters
    >>>caminho='/media/Rasters'
    >>>arquivo_HDF5='/media/dados_hdf.hdf5'
    #foramto dos rasters
    >>>formato = '.tif'    
    #Obter nomes dos rasters
    >>>proc=Converter_rasters_to_HDF5(caminho, formato)
    #obter os caminhos e os nomes dos rasters
    >>>proc.obterNomesRasters()
    #Converter cada raster para HDF5
    >>>f_hdf=proc.Converte_Rasters_to_HDF(arquivo_HDF5)
        
    >>> f_hdf.close()
    '''
    
    def __init__(self,caminho, formato):
        self.caminho=caminho
        self.formato=formato

        
    def obterNomesRasters(self):
        #armazena o caminho e o nome do raster
        self.caminho_nome_rasters = [[os.path.join(self.caminho,f),os.path.join(self.caminho,f).split('/')[-1].split('.')[0]] for f in os.listdir(self.caminho) if f.endswith(self.formato)]
        print self.caminho_nome_rasters[0][0]
        
    def leituraRaster(self,caminho_raster):
        self.caminho_raster=caminho_raster
        #Obter drives para todos os tipos de imagem
        gdal.AllRegister()
        #Get metadata image
        self.ds = gdal.Open(self.caminho_raster, gdal.GA_ReadOnly)
        #Total de colunas e linhas
        self.colunas= self.ds.RasterXSize
        self.linhas = self.ds.RasterYSize
        
    
    def Converte_Rasters_to_HDF(self,arquivo_HDF):
        
        '''
        #Cria um HDF5 a partir das imagens na pasta
        '''
        #Ler um raster
        self.leituraRaster(self.caminho_nome_rasters[0][0])
        #criar varuavel HDf
        self.arquivo_HDF=arquivo_HDF
        #criar arquivo HDF
        f_hdf = h5py.File(self.arquivo_HDF, "w",libver='latest')
        #Criar conjunto de dados HDF
        conjunto_dados = f_hdf.create_dataset('rasters', (self.linhas*self.colunas, \
        len(self.caminho_nome_rasters)), chunks=True,dtype=np.float32)
        print conjunto_dados.shape
        #percorrer cada raster e armazenar no HDF5
        for raster, arquivo_raster in enumerate (self.caminho_nome_rasters):
            print 'Nomes rasters: ',arquivo_raster[1]
            #Ler  raster
            self.leituraRaster(arquivo_raster[0])            
            #Ler o numero de bandas 
            nBands = self.ds.RasterCount
            print 'Bandas: ',nBands
            for nBand in range(1,nBands+1):
                #Read rasters how array
                print self.ds.GetRasterBand(nBand).ReadAsArray().reshape(-1).shape
                conjunto_dados[:,raster]=self.ds.GetRasterBand(nBand).ReadAsArray().reshape(-1)
            
        return f_hdf
        
        
#Pasta com os rasters
caminho='/home/ruiz/Documentos/TESTES/orto_img'
arquivo_HDF5='/home/ruiz/Documentos/TESTES/orto_img/orto1.hdf5'
#foramto dos rasters
formato = '.tif'    
#Obter nomes dos rasters
proc=Converter_rasters_to_HDF5(caminho, formato)
#obter os caminhos e os nomes dos rasters
proc.obterNomesRasters()
f_hdf=proc.Converte_Rasters_to_HDF(arquivo_HDF5)
f_hdf.close()

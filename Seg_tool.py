
# first we load every library or functionality we wild need otherwise
# a "this item is non defined error will raise"

from qgis.PyQt.QtCore import QCoreApplication, QVariant
from qgis.core import (QgsField, QgsFeature, QgsFeatureSink, QgsFeatureRequest, QgsProcessing, QgsProcessingAlgorithm, QgsProcessingParameterFeatureSource, QgsProcessingParameterFeatureSink,
    QgsProcessingParameterMultipleLayers,QgsProcessingParameterMatrix,QgsProcessingParameterFolderDestination,QgsProcessingParameterFileDestination,QgsProcessingParameterString,QgsProcessingParameterFile)
import os ,subprocess,glob, processing
from qgis.gui import QgsAbstractDataSourceWidget
import gdal_merge, sys, osr
from datetime import datetime
import shutil, gdal
import numpy as np
class ExAlgo(QgsProcessingAlgorithm):
    
    INPUT = 'INPUT'
    OUTPUT = 'OUTPUT'
    PATH_EXE='PATH_EXE'
    CELLSIZE='CELLSIZE'
    CLASS='CLASS'
    #C2A='Convert2Ascii'
    Lx2='Lx2'

    # gridmetrics
    MINHT='minht'
    FCC='FCC'
    ClasG='ClasG'

    #csv2grid

    COLUMN='COLUMN'
    #NODATA='NODATA'
    PIXEL='PIXEL'

    #NDVI
    INPUT_SEN = 'INPUT_SEN'

    # Meanshift
    PATH_BAT='PATH_BAT'
    SPATIALR='spatialr'
    RANGER='RANGER'
    MAXITER='MAXITER'
    MINSIZE='MINSIZE'

    # MULTIBAND RASTER
    MONTE='MONTE'


   
    def __init__(self):
        super().__init__()
 
    def name(self):
        return "Segmentation tool"
     
    def tr(self, text):
        return QCoreApplication.translate("Segmentation tool", text)
         
    def displayName(self):
        return self.tr("LiDAR and Sentinel Segmentation tool ")
 
    def group(self):
        return self.tr("TFM_QGIS3_ALG")
 
    def groupId(self):
        return "examples"
 
    def shortHelpString(self):
        return self.tr("This algorithm uses the FUSION Lidar processing software and the OTB library"
        "to create a tool that automatices LiDAR and Sentinel data processing. The output is a shapefile containing"
        "homogeneous forest sections to be suggested as forest stands. Additionally the tool offers as complementary outputs:"
        "\n\t· A digital elevation Model"
        "\n\t· A Multiband Raster, containing at least Dominan height, Canopy height, canopy cover information and NDVI index"
        "\n\t· A raster per band information"
        "\nOutputs will be stored in a foder with the name given by the user. temp+name for the temporal data; Productos_finales_+name for the final results")
 
    def helpUrl(self):
        return "https://qgis.org"
         
    def createInstance(self):
        return type(self)()
        
    # here we define all the inputs and output parameters. 
    # FeatureSource , allow us to choose from the files presetn in the canvas and in the computer
    # String you can introduce a string
    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterFolderDestination(
            self.INPUT,
            self.tr("Input .laz folder"),
            optional=True
            ))
        
        c=glob.glob(os.path.join('C:\\','*FUSION'))
        x=glob.glob(os.path.join('C:\\Program files\\','*FUSION'))
        
        str_c=''
        str_x=''
        for element in c:
            print(element)
            str_c= str_c+' '+element 
        
        for element in x:
            if element =='':
                pass
            else:
                str_x= str_x+' '+element
        lista=[str_c,str_x]


        for i in lista:
            if i != '':
                global path_exe
                path_exe=i
                break
            elif i == '':
                self.addParameter(QgsProcessingParameterFolderDestination(
                    self.PATH_EXE,
                    self.tr("Input Path FUSION folder")
                    ))
            
        self.addParameter(QgsProcessingParameterFileDestination(
            self.OUTPUT,
            self.tr("Output Folder Destination: input folder name"),
            fileFilter='.dtm'
            ))
        self.addParameter(QgsProcessingParameterString(
            self.CELLSIZE,
            self.tr("GridSurfaceCreate: MDE cellsize    Default [2]"),
            optional=True
            ))
        self.addParameter(QgsProcessingParameterString(
            self.CLASS,
            self.tr("GridSurfaceCreate: Classes to be processed in the MDE      Default [2]"),
            optional= True
            ))
       
        self.addParameter(QgsProcessingParameterString(
            self.Lx2,
            self.tr("Is yor LiDAR File 2000x2000? [2] or 1000x1000? [1]     Default [2]"),
            optional= True
            ))

        #gridmetrics
        self.addParameter(QgsProcessingParameterString(
            self.MINHT,
            self.tr("GridMetrics: Minimun height    Default [2]"),
            optional=True
            ))
        self.addParameter(QgsProcessingParameterString(
            self.FCC,
            self.tr("GidMetrics: FCC    Default [2]"),
            optional=True
            ))
        self.addParameter(QgsProcessingParameterString(
            self.ClasG,
            self.tr("Gridmetrics: Classes   Default [2,3,4,5]"),
            optional= True
            ))

        #csv2grid
        self.addParameter(QgsProcessingParameterString(
            self.COLUMN,
            self.tr("Gridmetrics Column: Select variable \tDefault [P90, P20, FCC]"),
            optional= True
            ))
     

        self.addParameter(QgsProcessingParameterString(
            self.PIXEL,
            self.tr("GridMetrics: Pixel Size    Default [20]"),
            optional=True
            ))

        # NDVI

        self.addParameter(
            QgsProcessingParameterFolderDestination(
                self.INPUT_SEN,
                self.tr('Input Sentinel folder'),
                optional=True
            ))

        # Multiband

        self.addParameter(QgsProcessingParameterFile(
            self.MONTE,
            self.tr("Study area shapefile. Mandatory when processing only Sentinel data"),
            optional=True
            ))
            
        # Meanshift
        otb=glob.glob(os.path.join('C:\\','*OTB-6.6.1-Win64'))
        PF=glob.glob(os.path.join('C:\\Program files\\','*OTB-6.6.1-Win64'))
        PF86=glob.glob(os.path.join('C:\\Program files (x86)\\','*OTB-6.6.1-Win64'))

        # find OTB path, if otb is not in list indicate the absolute path.


        str_otb=''
        str_pf=''
        str_pf86=''
        for element in otb:
            if element=='':
                pass
            else:
                print(element)
                str_otb= str_otb+' '+element 
        
        for element in PF:
            if element =='':
                pass
            else:
                str_pf= str_pf+' '+element
        for element in PF86:
            if element =='':
                pass
            else:
                str_pf86= str_pf86+' '+element
        lista=[str_otb,str_pf,str_pf86]


        for i in lista:
            if i != '':
                global path_bat
                path_bat=i
                break
            elif i == '':
                path_bat=''
                self.addParameter(QgsProcessingParameterFolderDestination(
                    self.PATH_BAT,
                    self.tr("Input Path OTB folder ")
                    ))

        self.addParameter(QgsProcessingParameterString(
            self.SPATIALR,
            self.tr("Meanshift: Spatial Radius     Default [5]"),
            optional=True
            ))
        self.addParameter(QgsProcessingParameterString(
            self.RANGER,
            self.tr("Meanshift: Range Radius   Default [15]"),
            optional= True
            ))
        self.addParameter(QgsProcessingParameterString(
            self.MAXITER,
            self.tr("Meanshift: Maximun iteration number   Default [100]"),
            optional= True
            ))

        self.addParameter(QgsProcessingParameterString(
            self.MINSIZE,
            self.tr("Meanshift: Minimun Region Size    Default [100]"),
            optional= True
            ))
 
    def processAlgorithm(self, parameters, context, feedback):
    # the parameters previously defined must be incorporated into the algorithm
    # msot of them are incorporated as Strings. We need to modify the strings afterwards
        source = self.parameterAsString(parameters, self.INPUT, context)
        global path_exe
        if path_exe!='':
        	pass
        else:
        	path_exe=self.parameterAsString(parameters, self.PATH_EXE,context)
        cellsize=self.parameterAsString(parameters, self.CELLSIZE,context)
        clas=self.parameterAsString(parameters, self.CLASS,context) 
        #c2a=self.parameterAsString(parameters, self.C2A,context)
        lx2=self.parameterAsString(parameters, self.Lx2,context)
        out=self.parameterAsFileOutput(parameters, self.OUTPUT,context)

        if lx2 == None or lx2 =='':
            lx2='2'
        elif lx2 not in ['1','2',None,'']:
            sys.exit('Introduce a correct input for file size 1 for 1000x1000 2 for 2000x2000. You introduced {}'.format(lx2))

        feedback.pushInfo('LiDAR file size: {}'.format(lx2))

        if ' ' in [source,out] or '´' in [source,out] or 'ñ' in [source,out]:
            sys.exit('\n\n\nLa ruta de los archivos .laz o la ruta de salida contiene espacios o caracteres especiales.\n')
        else:
            pass

        # requiered for gridmetrics
        minht=self.parameterAsString(parameters, self.MINHT,context) 
        fcc=self.parameterAsString(parameters, self.FCC,context)
        clasg=self.parameterAsString(parameters, self.ClasG,context)
        pixel=self.parameterAsString(parameters, self.PIXEL,context)

        #csv2grid
        col=self.parameterAsString(parameters, self.COLUMN,context)
        # add the dominant height the canopy height and the ccanopy cover by default
        ho_p20_fcc='49,36,27'
        col=ho_p20_fcc+col
        col=col.split(',')

        # vegetation index 
        source_sen = self.parameterAsString(parameters,self.INPUT_SEN,context)
        
        # multiband

        monte= self.parameterAsString(parameters,self.MONTE,context)


        if os.path.basename(source)=='INPUT' and os.path.basename(source_sen)=='INPUT_SEN':
            sys.exit('No input data. Please introduce LiDAR or Sentinel 2 data')
        
        
        # varaibles that obtaine the files needed en each process
        
        
        basename= os.path.basename(out).split('.dtm')[0]
        
        # path to folders
        o=os.path.dirname(out)
        feedback.pushInfo('source:{}'.format(source))
        feedback.pushInfo('source_sen:{}'.format(source_sen))

        # by defualt the non filled fields retrieve a path to a folder named after the class variables

        if os.path.basename(source_sen)=='INPUT_SEN':
            #LiDAR data
            o_temp=os.path.join(o,'temp_LiDAR_'+basename)
            o_raster=os.path.join(o_temp,'Rasters_LiDAR_'+basename)
            o_metric=os.path.join(o_temp,'Metrics_LiDAR_'+basename)
            o_MDE=os.path.join(o_temp,'MDE_LiDAR_'+basename)
            o_final=os.path.join(o,'Productos_finales_LiDAR_'+basename)
        elif os.path.basename(source)=='INPUT':
            #Sentinel data
            o_temp=os.path.join(o,'temp_Sentinel_'+basename)
            o_raster=os.path.join(o_temp,'Rasters_Sentinel_'+basename)
            o_metric=os.path.join(o_temp,'Metrics_Sentinel_'+basename)
            o_MDE=os.path.join(o_temp,'MDE_Sentinel_'+basename)
            o_final=os.path.join(o,'Productos_finales_Sentinel_'+basename)
        else:
            # Sentinel and LiDAR
            o_temp=os.path.join(o,'temp_'+basename)
            o_raster=os.path.join(o_temp,'Rasters_'+basename)
            o_metric=os.path.join(o_temp,'Metrics_'+basename)
            o_MDE=os.path.join(o_temp,'MDE_'+basename)
            o_final=os.path.join(o,'Productos_finales_'+basename)



        # outputs paths
        o_MDE_ba=os.path.join(o_MDE,basename)
        o_metric_ba=os.path.join(o_metric,basename)
        o_raster_ba=os.path.join(o_raster,basename)
        o_final_ba=os.path.join(o_final,basename)


        # create folders to store the results
        folders=[]
        for root, dirs, files in os.walk(o, topdown=False):
           for name in files:
              pass
              #print(os.path.join(root, name))
           for name in dirs:
              fold=(os.path.join(root, name))
              folders.append(fold)
       
        if o_temp in folders:
            pass
        else:
            os.mkdir(o_temp,1)
        if o_raster in folders:
            pass
        else:
            os.mkdir(o_raster,1)
        if o_MDE in folders:
            pass
        else:
            os.mkdir(o_MDE,1)
        if o_metric in folders:
            pass
        else:
            os.mkdir(o_metric,1)
        if o_final in folders:
            pass
        else:
            os.mkdir(o_final,1)
        
        LAS_files_folder= os.path.dirname(source) # LiDAR Files folder

        files= glob.glob(os.path.join(source,'*.laz'))

        
        if os.path.basename(source)=='INPUT':
            feedback.pushInfo('\n\t\tUSING SENTINEL DATA\n')
            shutil.rmtree(o_temp)
        else:
            # set default values in case there is LiDAR data of the compulsory parameters for LiDAR processing
            if minht=='':
                minht='2'
            else:
                pass
            if fcc=='':
                fcc='2'
            else:
                pass
            if clasg=='':
                clasg='2,3,4,5'#gridmetrics classes
            else:
                pass
            if pixel =='':
                pixel='20'#gridmetrics processing
            else:
                pass
            if cellsize=='':
                cellsize='2'#MDE size
            else:
                pass
            if clas =='':
                clas='2'#MDE classes
            else:
                pass

            feedback.pushInfo('LiDAR parameter values:\n · minht:{} \n · fcc:{}\n · GridMetrics classes:{}\n · GridMetrics pixelsize:{}\n · GridSurfaceCreate cellsize:{} \n · GridSurfaceCreate classes:{}'.format(minht,fcc,clasg,pixel,cellsize,clas))

            for i,file in enumerate(files):
                if feedback.isCanceled():
                    sys.exit('Process Canceled')
            
                # extract the file name
                nombre=os.path.basename(file)
                #reverse the string as the standar name is more stable at the end
                file=file[::-1]
                # get x and y 
                y=file[16:20]
                x=file[21:24]
                # reverse the strings back to normal 
                x=int(x[::-1])
                y=int(y[::-1])
                file=file[::-1]

                filename = os.path.join(source, str(x)+'-'+str(y)+"_lista_de_archivos.txt")
                #create the text files where the 9 .laz files will be stored and passed on to FUSION
                Txtfile = open(filename, 'w')

                if lx2 == '2':
                    # calculate inital coordiante where the iteration begins
                    c_ini=[x*1000,y*1000-2000]
                    c_fin=[x*1000+2000,y*1000]
                    # calculate buffer's inital  coordinate
                    c_ini_buf=[c_ini[0]-200,c_ini[1]-200]
                    # amount of cells (height and width) in the buffer 2400 m - 20 m of pixel size
                    # numero de celdas de alto y ancho del buffer 2400 metros -20 m de tamaño de pixel
                    t_pix=2
                    W=2400-t_pix
                    H=2400-t_pix
                    comando_switchgrid='/grid:'+str(c_ini_buf[0])+','+str(c_ini_buf[1])+','+str(W)+','+str(H)
                    comando_buffer='/grid:'+str(c_ini_buf[0])+','+str(c_ini_buf[1])+','+str(W)+','+str(H)
                    # obtain the files names that sorrounds the file "file" in the iteration. Next the MDE will be created.
                    files_list=[str(x-2)+'-'+str(y+2),str(x)+'-'+str(y+2),str(x+2)+'-'+str(y-2),
        				        str(x-2)+'-'+str(y),str(x)+'-'+str(y),str(x+2)+'-'+str(y),
        				        str(x-2)+'-'+str(y-2),str(x)+'-'+str(y-2),str(x+2)+'-'+str(y-2)]
                        
                   
                else:
                    c_ini=[x*1000,y*1000-1000]
                    c_fin=[x*1000+1000,y*1000]
                    # calculate buffer's inital  coordinate
                    c_ini_buf=[c_ini[0]-200,c_ini[1]-200]
                    
                    # amount of cells (height and width) in the buffer 2400 m - 20 m of pixel size
                    # numero de celdas de alto y ancho del buffer 2400 metros -20 m de tamaño de pixel
                    t_pix=2
                    W=1400-t_pix
                    H=1400-t_pix
                    comando_switchgrid='/grid:'+str(c_ini_buf[0])+','+str(c_ini_buf[1])+','+str(W)+','+str(H)
                    comando_buffer='/grid:'+str(c_ini_buf[0])+','+str(c_ini_buf[1])+','+str(W)+','+str(H)
                    
                    # obtain the files names that sorrounds the file "file" in the iteration. Next the MDE will be created.  
                    files_list=[str(x-1)+'-'+str(y+1),str(x)+'-'+str(y+1),str(x+1)+'-'+str(y-1),
                                str(x-1)+'-'+str(y),str(x)+'-'+str(y),str(x+1)+'-'+str(y),
                                str(x-1)+'-'+str(y-1),str(x)+'-'+str(y-1),str(x+1)+'-'+str(y-1)]
                
                root=file.split('.laz')[0]
                no_ext_fn=root.split('_')
                tail='_'+no_ext_fn[-1]
                
                #get common part of the file name
                common_name_part="_".join(no_ext_fn[:-2])+"_"     

                
                for item in files_list:
                    arch=common_name_part+item+tail+'.laz'
                    Txtfile.write('{}\n'.format(arch)) #Escribir en el fichero de comandos
                Txtfile.close()

                #define the folders where the files and .exes are
                
                dtm_filename =o_MDE_ba+'_'+str(x)+'-'+str(y)+'.dtm'
                ascii_filename =o_MDE_ba+'_'+str(x)+'-'+str(y)+'.asc'
                commands = [os.path.join(path_exe,'GridSurfaceCreate.exe')]
                string= path_exe+'\\GridSurfaceCreate.exe'
                
                #Switches
                commands.append('/verbose')
                string= string +' '+comando_buffer
                commands.append(comando_buffer)
            
                if str(clas).strip() != '':
                    commands.append('/class:'+ str(clas))
                    string=string+' /class:'+ str(clas)+' '
             
                #Parameters needed:
                commands.append(os.path.join(source, dtm_filename))
                commands.append(str(cellsize))
                commands.append('m')
                commands.append('m')
                commands.append('0')
                commands.append('0')
                commands.append('0')
                commands.append('0')  
                commands.append(filename)#os.path.join(LAS_files_folder, source))
                string= string+' '+dtm_filename+' '+cellsize+' m m 0 0 0 0 '+filename
                
                    
                
                feedback.pushInfo('\ncomando GridSurfaceCreate: {}'.format(string))

                proc = subprocess.run(string, shell=True)

                #ClipDTM [switches] InputDTM OutputDTM MinX MinY MaxX MaxY
                

                commands=[os.path.join(path_exe,'ClipDTM.exe')]
                commands.append(dtm_filename)

                clip_filename =o_MDE_ba+'_'+str(x)+'-'+str(y)+'_clip'+'.dtm'
                asclip_filename=o_MDE_ba+'_'+str(x)+'-'+str(y)+'_clip'+'.asc'
                commands.append(clip_filename)
                #Min X 
                commands.append(str(c_ini[0]))
                # Min Y 
                commands.append(str(c_ini[1]))
                # Max X 
                commands.append(str(c_fin[0]))
                # Max Y
                commands.append(str(c_fin[1]))

                minx=str(c_ini[0])
                miny=str(c_ini[1])
                maxx=str(c_fin[0])
                maxy=str(c_fin[1])

                string=path_exe+'\\ClipDTM.exe'+' '+dtm_filename+' '+clip_filename+' '+minx+' '+miny+' '+maxx+' '+maxy
                
                feedback.pushInfo('comando ClipDTM: {}'.format(string))

                proc=subprocess.run(string,shell=True)


                # turn dtm into asc


                commands = [os.path.join(path_exe, 'DTM2ASCII.exe')]
                commands.append(clip_filename)
                commands.append(ascii_filename)
                string=path_exe+'\\DTM2ASCII.exe'+' '+clip_filename+' '+asclip_filename

                feedback.pushInfo('\ncomando DTM2ASCII: {}'.format(string))
         
                proc = subprocess.run(string, shell=True)
                #proc.wait() #Crear .asc

                # -------------------------    
                #       GRIDMETRICS 
                # -------------------------

                archivos=glob.glob(os.path.join(o_MDE,'*clip.dtm'))# dtm fold out de la primera 

                #define the folders where the files and .exes are
                
                csv_filename =o_metric_ba+'_'+str(x)+'-'+str(y)+'.csv'
                commands = [os.path.join(path_exe,'gridmetrics.exe')]
                string=path_exe+'\\gridmetrics.exe'
                
                #Switches
                commands.append('/verbose')

                # grid switch
                commands.append(comando_switchgrid)
                string= string+' /verbose'+' '+comando_switchgrid
                
                if str(minht).strip() != '':
                    commands.append('/minht:'+ str(minht))
                    string=string+ ' /minht:'+ str(minht)
                if str(clas).strip() != '':
                    commands.append('/class:'+ str(clasg))
                    string=string+ ' /class:'+ str(clasg)
                string=string+' /outlier:-1,40'
             
                #Parameters requiered:
                # clip.dtm file 
                commands.append(archivos[i])
                # fcc and pixel size
                commands.append(str(fcc))
                commands.append(str(pixel))
                #output csv  
                commands.append(csv_filename)
                # txt files with the 9 laz files
                commands.append(file)

                
                string=string+' '+archivos[i]+' '+fcc+' '+pixel+' '+csv_filename+' '+file

                feedback.pushInfo('\ncomando Gridmetrics: {}'.format(string))
                proc = subprocess.run(string, shell=True)


                # -------------------------    
                #       CSV2GRID 
                # -------------------------

            metrics= glob.glob(os.path.join(o_metric,'*all_returns_elevation_stats.csv'))#source = out gridmetrics
            
            o=os.path.dirname(out)
            
            

            fvar=["Row","Col","Center","Center","Total_return_count_above_htmin","Elev_minimum",
            "Elev_maximum","Elev_mean","Elev_mode","Elev_stddev","Elev_variance","Elev_CV",
            "Elev_IQ_Int_IQ","Elev_skewness","Elev_kurtosis","Elev_AAD","Elev_L1","Elev_L2",
            "Elev_L3","Elev_L4","Elev_L_CV","Elev_L_skewness","Elev_L_kurtosis","Elev_P01",
            "Elev_P05","Elev_P10","Elev_P20","Elev_P25","Elev_P30","Elev_P40","Elev_P50",
            "Elev_P60","Elev_P70","Elev_P75","Elev_P80","Elev_P90","Elev_P95","Elev_P99",
            "Return_1_count_above_htmin","Return_2_count_above_htmin","Return_3_count_above_htmin",
            "Return_4_count_above_htmin","Return_5_count_above_htmin","Return_6_count_above_htmin",
            "Return_7_count_above_htmin","Return_8_count_above_htmin","Return_9_count_above_htmin",
            "Other_return_count_above_htmin","Percentage_first_returns_above_heightbreak","Percentage_all_returns_above_heightbreak",
            "(All_returns_above_heightbreak)/(Total_first_returns)*100","First_returns_above_heightbreak","All_returns_above_heightbreak",
            "Percentage_first_returns_above_mean","Percentage_first_returns_above_mode","Percentage_all_returns_above_mean","Percentage_all_returns_above_mode",
            "(All_returns_above_mean)/(Total_first_returns)*100","(All_returns_above_mode)/(Total_first_returns)*100","First_returns_above_mean","First_returns_above_mode",
            "All_returns_above_mean","All_returns_above_mode","Total_first_returns","Total_all_returns","Elev_MAD_median","Elev_MAD_mode","Canopy_relief_ratio((mean_-_min)/(max_–_min))",
            "Elev_quadratic_mean","Elev_cubic_mean","KDE_elev_modes","KDE_elev_min_mode","KDE_elev_max_mode","KDE_elev_mode_range"]
                            
            for i,metric in enumerate(metrics):
                for c in col:
                # extract the file name
                    c=int(c)-1
                    nombre=os.path.basename(metric)
                    
                    asc_filename =o_raster_ba+'_'+nombre.split('all_returns_elevation_stats.csv')[0]+str(fvar[int(c)])+'.asc'
                    commands = [os.path.join(path_exe,'CSV2Grid.exe')]
                    string= path_exe+'\\CSV2Grid.exe'
                    
                    #Switches
                    commands.append('/verbose')
                 
                    #Parametros necesarios:
                    # input
                    commands.append(metric)
                    # columna
                    c=int(c)+1
                    commands.append(str(c))
                    #salida csv  
                    commands.append(asc_filename)
                    string=string+' '+metric+' '+str(c)+' '+asc_filename

                    feedback.pushInfo('\ncomando CSV2Grid: {}'.format(string))
                                       
                    proc = subprocess.Popen(string, shell=True)
                    proc.wait() #Crear .dtm
                

            # join the .asc
            for c in col:
                c=int(c)-1
                variable=glob.glob(os.path.join(o_raster,'*'+str(fvar[int(c)])+'.asc'))
                

                if str(pixel).strip() != '':
                    variable.append('-ps')
                    variable.append(pixel)
                    variable.append(pixel)

                variable.append('-a_nodata')
                variable.append(str(-9999))
            

                out=o_final_ba+'_merged_'+str(fvar[int(c)])+'.tif'
                variable.append('-o')
                variable.append(out)
                variable.insert(0,'')
                c=int(c)+1

        
                feedback.pushInfo('\ncomando merge: {}'.format(variable))

                gdal_merge.main(variable)

                

            # merged asc files in one GRIDSURFACE CREATE

            merged=glob.glob(os.path.join(o_MDE,'*_clip.asc'))
                    
            merged.append('-a_nodata')
            merged.append(str(-9999))
            out=o_final_ba+'_MDE_merged.tif'
            merged.append('-o')
            merged.append(out)
            merged.insert(0,'')
     
            gdal_merge.main(merged)


        # -------------------------    
        #     VEGETATION INDEX 
        # -------------------------

        # Create vegetation index. First, look fot the satellite scenes in the folder, second, call processing algorithm.

        out_vegind=o_final_ba+'_NDVI.tif'
        if os.path.basename(source_sen)=='INPUT_SEN':
            feedback.pushInfo('\n\t\tUSING LIDAR DATA\n')
            if monte=='MONTE':
                sys.exit('Study area shape file is requiered. Please introduce the shapefile')
            else:
                pass
        else:
            satelite_img=glob.glob(os.path.join(source_sen,'*.jp2'))
            for img in satelite_img:
                if 'B02' in img:
                    blue=img
                elif 'B03' in img:
                    green=img
                elif 'B04' in img:
                    red=img
                elif 'B05' in img:
                    B05=img
                elif 'B07' in img:
                    B07=img
                elif 'B8A' in img:
                    nir=img


            buffered_layer = processing.run("grass7:i.vi", {
                'GRASS_RASTER_FORMAT_META' : '', 
                'GRASS_RASTER_FORMAT_OPT' : '', 
                'GRASS_REGION_CELLSIZE_PARAMETER' : 0, 
                'GRASS_REGION_PARAMETER' : None, 
                'band5' : B05, 
                'band7' : B07, 
                'blue' : blue, 
                'green' : green, 
                'nir' : nir, 
                'output' : out_vegind, 
                'red' : red, 
                'soil_line_intercept' : None, 
                'soil_line_slope' : None, 
                'soil_noise_reduction' : None, 
                'storage_bit' : 1, 
                'viname' : 10 
            }, context=context, feedback=feedback)['output']


            # -------------------------    
            #   Clip Vegetation index
            # -------------------------



            s= glob.glob(os.path.join(o_final,'*NDVI.tif'))# salida del anterior
            s=s[0]
             # we use as mask one of the clipped asc with the variable information.
            if os.path.basename(source)=='INPUT':
                clip=monte
            else:
                clip_var=int(col[0])-1
                clip = glob.glob(os.path.join(o_final,'*'+str(fvar[int(clip_var)])+'*.tif'))
                clip=clip[0]
            out = o_final_ba+'_NDVI_clip.tif'
            
            
            
            buffered_layer = processing.run("gdal:cliprasterbyextent", {
                'INPUT': s,
                'DATA_TYPE': 0,
                'NODATA': -9999,
                'OPTIONS': '',
                'PROJWIN': clip,
                'OUTPUT': str(out)
            }, context=context, feedback=feedback)['OUTPUT']


        

        ### ------------------------------------------
        ###                 NORMALIZATION
        ### ------------------------------------------

        


        # check that only LiDAR raster variables and NDVI are in the list    
        source = glob.glob(os.path.join(o_final,'*.tif'))
        source_NDVI=glob.glob(os.path.join(o_final,'*_NDVI.tif'))
        source_MDE=glob.glob(os.path.join(o_final,'*_MDE_merged.tif'))

        source_multi=glob.glob(os.path.join(o_final,'*_multiband.tif'))
        
        # when LiDAR data is not null
        if source_MDE!=[]:
            source_NDVI.append(source_MDE[0])
        else:
            pass
            
        # remove multiband raster if exists and MDE_merged raster from the list
        for i in source:
            if i in source_NDVI or i in source_multi:
                source.remove(i)
            else:
                pass
        #order bands alphabetically
        source.sort()

        for raster in source:

            RasterSource = gdal.Open(raster)
            rows =RasterSource.RasterYSize # number of pixels in y
            cols = RasterSource.RasterXSize # number of pixels in x
            print('Processing: {}\nrows: {}, cols: {} '. format(raster,rows,cols))
            geoTransform=RasterSource.GetGeoTransform()
            band = RasterSource.GetRasterBand(1)
            data=band.ReadAsArray(0, 0, cols, rows)
            n_width= range(rows)
            n_heigth= range(cols)

            geoTransform=RasterSource.GetGeoTransform()
            pixelWidth = geoTransform[1]
            pixelHeight= geoTransform[5]
            originX = geoTransform[0]
            originY = geoTransform[3]

            newRasterfn=raster.split('.tif')[0]+'_norm.tif'
            #obtaining info from each raster and band
            array=[]
            if 'NDVI' in raster:
                for x in n_width:
                    for y in n_heigth:
                        aux= float(data[x,y])
                        if aux==-9999:
                            aux=-9999
                            array.append(aux)
                        elif -1<aux<0:
                            aux=0
                            array.append(aux)
                        else:
                            array.append(aux)
            else:
                for x in n_width:
                    for y in n_heigth:
                        aux= float(data[x,y])
                        if aux==-9999:
                            aux=-9999
                            array.append(aux)
                        else:
                            array.append(aux)
            #store raster data in an array
            # obtain raster max value
            values=[]
            for value in array:
                #print(value)
                if value!=None:
                    values.append(value)
                else:
                    pass
            #print('values',values)
            max_val=max(values)

            p75=np.percentile(values,75)
            p90=np.percentile(values,90)

            print('valor maximo de {}: {} \t p75:{}'.format(os.path.basename(newRasterfn),max_val,p90))
            # reclasify raster  from 0-100.
            lista_nueva = []
            lista_norm=[]
            # conversion ndvi
            min_value=min(values)
            for elemento in array:
                
                if elemento==None:
                    lista_norm.append(-9999)
                elif elemento==0:
                    lista_norm.append(0)
                elif elemento==-9999:
                    lista_norm.append(-9999)
                else:
                    if 'P90' in raster or 'P20' in raster:
                        if elemento < p90:
                            elem_norm=((elemento-2)/(p90-2))*100
                            lista_norm.append(elem_norm)
                        else:
                            lista_norm.append(100)
                    #elif 'Percentage_first_returns_above_heightbreak' in raster:
                    #   lista_norm.append(elemento)
                    else:
                        elem_norm=(elemento/max_val)*100
                        lista_norm.append(elem_norm)
                
                
            # Create numpy array required for gdal WriteArray comand
            # give the array a strucutre
            es=[cols,rows]
            estructura=max(es)
            for i in range(0, len(lista_norm), cols):
                lista_nueva.append(lista_norm[i:i+cols])
            array_norm = np.array(lista_nueva)
            #array_norm=array_norm[::-1]
            print(cols)

            driver = gdal.GetDriverByName('GTiff')
            outRaster = driver.Create(newRasterfn, cols, rows, 1, gdal.GDT_Float32)
            outRaster.SetGeoTransform((originX, pixelWidth, 0, originY, 0, pixelHeight))
            outband = outRaster.GetRasterBand(1)
            outband.WriteArray(array_norm)
            outRasterSRS = osr.SpatialReference()
            outRasterSRS.ImportFromEPSG(25830)
            outRaster.SetProjection(outRasterSRS.ExportToWkt())
            outband.FlushCache()


        norm_source=[]
        for i in source:
            if 'Percentage_first_returns_above_heightbreak'in i:
                norm_source.append(i)
            else:
                norm_file=i.split('.tif')[0]+'_norm.tif'
                norm_source.append(norm_file)



        merged=norm_source
        print('\n',merged)
        merged.append('-separate')

        merged.append('-n')
        merged.append(str(-9999))

        merged.append('-a_nodata')
        merged.append(str(-9999))


        out=o_final_ba+'_multiband.tif'
        merged.append('-o')
        merged.append(out)
        merged.insert(0,'')

        gdal_merge.main(merged)

        for raster in norm_source:
            if '_norm' in raster or 'Percentage_first_returns_above_heightbreak_norm' in raster:
                os.remove(raster)
            else:
                pass



        #-----------------------------------
        #       Segmentation meanshift
        #-----------------------------------

        # checks if the path exisits. If so, adds the path to the segmentation .bat. If not, the user will have to specify the path to the OTB folder.

        global path_bat
        if path_bat!='':
            path_bat=path_bat+'\\bin\\otbcli_Segmentation.bat'
            pass
        else:
            path_bat=self.parameterAsString(parameters, self.PATH_BAT,context)
            path_bat=path_bat+'\\bin\\otbcli_Segmentation.bat'

        spatialr=self.parameterAsString(parameters, self.SPATIALR,context)
        ranger=self.parameterAsString(parameters, self.RANGER,context) 
        maxiter=self.parameterAsString(parameters, self.MAXITER,context)
        minsize=self.parameterAsString(parameters, self.MINSIZE,context)
        out=o_final_ba+'_meanshift_segmentation.shp'

        o=os.path.dirname(out)
        if len(norm_source)==1:
            feedback.pushInfo('NDVI_norm')
            source=o_final_ba+'_NDVI_clip_norm.tif'
        else:
            source=glob.glob(os.path.join(o_final,'*_multiband.tif'))
            source=source[0]
        
    
        # bat path

        commands = [path_bat]
        # input
        commands.append('-in')
        commands.append(source)
        # output
        commands.append('-mode.vector.out')
        commands.append(out)

        string=path_bat+' -in '+source+' -mode.vector.out '+out 

        #Parametros necesarios:

        if str(spatialr).strip() != '':
            commands.append('-filter.meanshift.spatialr '+ str(spatialr))
            string= string +' -filter.meanshift.spatialr '+ str(spatialr)
        if str(ranger).strip() != '':
            commands.append('-filter.meanshift.ranger '+ str(ranger))
            string= string +' -filter.meanshift.ranger '+ str(ranger)
        if str(minsize).strip() != '':
            commands.append('-filter.meanshift.minsize '+ str(minsize))
            string=string+ ' -filter.meanshift.minsize '+ str(minsize)
        if str(maxiter).strip() != '':
            commands.append('-filter.meanshift.maxiter '+ str(maxiter))
            string=string+ ' -filter.meanshift.maxiter '+ str(maxiter)            
            
        # it seems that when shell=True it is better to pass the args as string rather that sequence 

        feedback.pushInfo('\ncomando meanshift: {}'.format(string))   
        proc = subprocess.Popen(string, shell=True)
        proc.wait() #Crear .dtm
        

        #-------------------------------------
        # Chaiken generalizacion de contornos
        #------------------------------------

        # dictionary returned by the processAlgorithm function.
        source=glob.glob(os.path.join(o_final,'*_meanshift_segmentation.shp'))
        source=source[0]

        sink= o_final_ba+'_rodales_chaiken.shp'
        error=o_final_ba+'error_snakes.gpkg'
        error_chai=o_final_ba+'error_chaiken.gpkg'
        
        buffered_layer = processing.run("grass7:v.generalize", {
            '-l' : True, 
            '-t' : False, 
            'GRASS_MIN_AREA_PARAMETER' : 0.0001,
            'GRASS_OUTPUT_TYPE_PARAMETER' : 0,
            'GRASS_REGION_PARAMETER' : None, 
            'GRASS_SNAP_TOLERANCE_PARAMETER' : -1, 
            'GRASS_VECTOR_DSCO' : '', 
            'GRASS_VECTOR_LCO' : '', 
            'alpha' : 1, 
            'angle_thresh' : 3, 
            'beta' : 1, 
            'betweeness_thresh' : 0, 
            'cats' : '', 
            'closeness_thresh' : 0,
            'degree_thresh' : 0,
            'error' : error_chai, 
            'input' : source, 
            'iterations' : 1, 
            'look_ahead' : 7, 
            'method' : 8, 
            'output' : sink, 
            'reduction' : 50, 
            'slide' : 0.5, 
            'threshold' : 1, 
            'type' : [0,1,2], 
            'where' : ''
        }, context=context, feedback=feedback)['output']


        sink= o_final_ba+'_rodales_snakes.shp'
        smoothing_snakes=processing.run('grass7:v.generalize',{ 
            '-l' : True, 
            '-t' : False, 
            'GRASS_MIN_AREA_PARAMETER' : 0.0001, 
            'GRASS_OUTPUT_TYPE_PARAMETER' : 0, 
            'GRASS_REGION_PARAMETER' : None,
            'GRASS_SNAP_TOLERANCE_PARAMETER' : -1, 
            'GRASS_VECTOR_DSCO' : '', 
            'GRASS_VECTOR_LCO' : '', 
            'alpha' : 1, 
            'angle_thresh' : 3, 
            'beta' : 1, 
            'betweeness_thresh' : 0, 
            'cats' : '',
            'closeness_thresh' : 0, 
            'degree_thresh' : 0, 
            'error' :error, 
            'input' : source, 
            'iterations' : 1, 
            'look_ahead' : 7, 
            'method' : 10,
            'output' : sink, 
            'reduction' : 50, 
            'slide' : 0.5, 
            'threshold' : 1, 
            'type' : [0,1,2], 
            'where' : '' 
            }, context=context, feedback=feedback)['output']


        feedback.pushInfo('\nPROCESO FINALIZADO')
    

                
                
        return {self.OUTPUT:sink}
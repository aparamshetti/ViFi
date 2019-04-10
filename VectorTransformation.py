import numpy as np
from keras import Model
from keras.layers import Conv2D,Conv2DTranspose,Dense,Input, merge, Add, Reshape
from keras.preprocessing.image import ImageDataGenerator
import glob,cv2
from keras import backend, Sequential,optimizers
import keras.applications as app
from keras import regularizers,initializers
import glob
from keras.models import load_model
import pandas as pd


class ConvertToVector:
    def __init__(self,path,file,layer_name="vector_layer",dtype = 'float16'):
        self._model = None
        self._path = path
        self._file = file
        self.layer_name = layer_name
        self._data_gen = None
        self._train_gen = None
        self.image_set = self._get_image_names()
        self.fib_dict = {}
        self.special_num = []
        self.inverted_index = {}
        self.fp_index = {}
        backend.set_floatx(dtype)
        
    def _train_model(self, batch_size = 32, epochs = 30, model_type = "vgg16"):  
        
        if model_type == "vgg16":
            self._construct_model_vgg16()
            data_gen = ImageDataGenerator(samplewise_center=False,samplewise_std_normalization=True,rotation_range=0, 
                                          width_shift_range=0,height_shift_range=0,horizontal_flip=False, zca_whitening= False)
            train_gen = data_gen.flow_from_directory(self._path,target_size=(224,224),batch_size=batch_size,class_mode='input',shuffle=True,seed = 100)
            
        elif model_type =="convDeconv":
            self._construct_model_conv_deconv()
            
            data_gen = ImageDataGenerator(samplewise_center=False,samplewise_std_normalization=True,rotation_range=0, 
                                          width_shift_range=0,height_shift_range=0,horizontal_flip=False, zca_whitening= False)
            train_gen = data_gen.flow_from_directory(self._path,target_size=(640,480),batch_size=batch_size,class_mode='input',shuffle=True,seed = 100)
            
            

        print(len(self.image_set))
        self._model.fit_generator(train_gen, steps_per_epoch = len(self.image_set)//batch_size, epochs = epochs)
        self._model.save("C:\\Users\\Jason\\Desktop\\Spring 2019\\Information retreival\\Project\\model.h5")
        
#     def _train_model(self, batch_size=1000, cut_off = 100000):
#         image_set = self._get_image_names()
#         len_image_set = min(len(image_set),cut_off)
#         if len_image_set < batch_size:
#             batch_size = len_image_set
#         self._construct_model()
#         inner_index = 0
#         outer_index = inner_index + batch_size
#         
#         while outer_index < len_image_set:    
#             print("inner: ", inner_index)
#             print("outer: ",outer_index)
#             img = cv2.imread(image_set[0])
# 
#            # x = []
#             y = []
#             while inner_index < outer_index:           
#                 img = cv2.imread(image_set[inner_index])
#                 norm_image = cv2.normalize(img, None, alpha=0, beta=1, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_32F)
#                 img = cv2.resize(norm_image,(224,224))
#               #  x.append(norm_image)
#                 y.append(img)
#                 inner_index+=1
#             
#          #   x_train = np.array(x)
#             y_train = np.array(y)
#             
# 
#             print("Fitting model: ")
#             
#             self._model.fit(y_train,y_train,batch_size = 64)
#             if outer_index + batch_size > len_image_set:
#                 outer_index = len_image_set
#             else:
#                 outer_index+=batch_size
#                 
#             del y_train , y
# 
#         return image_set
# =============================================================================
            
    def _get_image_names(self):
        path = self._path+"\\"+self._file + "\\Images\\*.jpg"
        file_list = glob.glob(path)
        return file_list
    
    
    def _construct_model_vgg16(self):
        
        vgg16 = app.vgg16.VGG16()
        chop_num = 4
        
        for num in range(chop_num):
            vgg16.layers.pop()
            
        
        for layer in vgg16.layers:
            layer.trainable = False
        
        last_layer = vgg16.get_layer("block5_pool").output

        
        layer_1 = Conv2DTranspose(filters = 512, kernel_size= 4, strides=(1,1), padding= "valid", activation = "relu", name = "vector_layer",kernel_regularizer=regularizers.l2(0.01), kernel_initializer=initializers.RandomNormal(stddev=0.1))(last_layer)
        layer_2 = Conv2DTranspose(filters = 256, kernel_size= 4, strides=(2,2), padding= "valid", activation = "relu",kernel_regularizer=regularizers.l2(0.01), kernel_initializer=initializers.RandomNormal(stddev=0.1))(layer_1)
        layer_3 = Conv2DTranspose(filters = 128, kernel_size= 5, strides=(1,1), padding= "valid", activation = "relu",kernel_regularizer=regularizers.l2(0.01), kernel_initializer=initializers.RandomNormal(stddev=0.1))(layer_2)
        layer_4 = Conv2DTranspose(filters = 64, kernel_size= 4, strides=(2,2), padding= "valid", activation = "relu",kernel_regularizer=regularizers.l2(0.01), kernel_initializer=initializers.RandomNormal(stddev=0.1))(layer_3)
        layer_5 = Conv2DTranspose(filters = 32, kernel_size= 4, strides=(2,2), padding= "valid", activation = "relu",kernel_regularizer=regularizers.l2(0.01), kernel_initializer=initializers.RandomNormal(stddev=0.1))(layer_4)
        layer_6 = Conv2DTranspose(filters = 16, kernel_size= 3, strides=(1,1), padding= "valid", activation = "relu",kernel_regularizer=regularizers.l2(0.01), kernel_initializer=initializers.RandomNormal(stddev=0.1))(layer_5)
        layer_7 = Conv2DTranspose(filters = 3, kernel_size= 2, strides=(2,2), padding= "valid", activation = "tanh",kernel_initializer=initializers.RandomNormal(stddev=0.1))(layer_6)
        
        
        self._model = Model(input = vgg16.input, output = layer_7)
        self._model.summary()
        sgd = optimizers.SGD(lr=0.01)
        self._model.compile(optimizer=sgd,loss='mean_squared_error',metrics=['accuracy'])
        
        return True
        
    
    def _construct_model_conv_deconv(self):
        self._model = Sequential()
        self._model.add(Conv2D(filters = 32, input_shape = (640,480,3), kernel_size=(5,3), strides=(2,2), activation="relu", kernel_initializer=initializers.RandomNormal(stddev=0.1)))
        self._model.add(Conv2D(filters = 64, kernel_size=(3,2), strides=(2,2), activation="relu", kernel_initializer=initializers.RandomNormal(stddev=0.1)))
        self._model.add(Conv2D(filters = 128, kernel_size=(3,3), strides=(2,2), activation="relu", kernel_initializer=initializers.RandomNormal(stddev=0.1)))
        self._model.add(Conv2D(filters = 1, kernel_size=(2,2), strides=(2,2), activation="relu", name=self.layer_name, kernel_initializer=initializers.RandomNormal(stddev=0.001)))
        self._model.add(Conv2DTranspose(filters = 128, kernel_size=(2,2), strides=(2,2), activation="relu", kernel_initializer=initializers.RandomNormal(stddev=0.001)))
        self._model.add(Conv2DTranspose(filters = 64, kernel_size=(2,2), strides=(2,2), activation="relu", kernel_initializer=initializers.RandomNormal(stddev=0.1)))
        self._model.add(Conv2DTranspose(filters = 32, kernel_size=(9,10), strides=(2,2), activation="relu", kernel_initializer=initializers.RandomNormal(stddev=0.1)))
        self._model.add(Conv2DTranspose(filters = 3, kernel_size=(4,2), strides=(2,2), activation="relu",kernel_initializer=initializers.RandomNormal(stddev=0.1)))
        
        sgd = optimizers.SGD(lr=0.001, decay=0.0001, momentum=0.8, nesterov=False)
        self._model.compile(optimizer="adagrad",loss='mean_squared_error',metrics=['accuracy'])
        self._model.summary()
        
        return True
        
            
    def _vectorize(self,img):
        
        intermediate_layer_model = Model(inputs=self._model.input,
                                 outputs=self._model.get_layer(self.layer_name).output)
        intermediate_output = intermediate_layer_model.predict(cv2.imread(img).reshape(1,640,480,3))
        
        return intermediate_output.flatten()
    
    def fib(self,n):
        if n in self.fib_dict:
            return self.fib_dict[n]
        if n == 0 or n == 1:
            self.fib_dict[n] = 1
            return 1
        else:
            r = self.fib(n-1)+self.fib(n-2)
            self.fib_dict[n] = r
            return r


    def _special_number_generator(self,n=1131):
        for i in range(n):
            x = (self.fib(i)+i)
            if x % (i+1) == 0:
                self.special_num.append(x%(i+2))
            else:
                self.special_num.append(x%(i+1))
        
        self.special_num = np.array(self.special_num).reshape(1131,1)
        return True
    
    def finger_print(self):
        self._special_number_generator()
        for i,img in enumerate(self.image_set):
            vec = self._vectorize(img)
            fp = vec.reshape(1,1131).dot(self.special_num)
            name = img.split('\\')[-1]
            self.inverted_index[name] = vec
            self.fp_index[name] = [fp]
            if i % 100 == 0:
                pd.DataFrame.from_dict(self.inverted_index).to_csv(self._path+"//inverted_index.csv",index=False)
                pd.DataFrame.from_dict(self.fp_index).to_csv(self._path+"//finger_print.csv",index=False)
            print("Completed: ",i)

    def main(self):
        
        if len(glob.glob(self._path+"\\*.h5")) > 0:
            self._model = load_model(path+"\\model.h5")
            print("Loaded model")
        else:
            #vec._train_model(32)
            vec._train_model(batch_size=64,model_type="convDeconv")
            
        self.finger_print()


        
if __name__ == "__main__":
    #path = "C:\\Users\\Jason\\Desktop\\Spring 2019\\Information retreival\\Project\\Snapshots\\"
    path = "C:\\Users\\Jason\\Desktop\\Spring 2019\\Information retreival\\Project\\"
    file = "Snapshot_1_3sec\\"
    vec = ConvertToVector(path,file)
    vec.main()
    
    
# =============================================================================
#     image_set = vec._train_model(32)
#     #image_set = vec._train_model(batch_size=64,model_type="convDeconv")
#     vec._model = load_model("C:\\Users\\Jason\\Desktop\\Spring 2019\\Information retreival\\Project\\model.h5")
#     vec.finger_print()
#     
#     d = {}
#     df = pd.DataFrame(columns=["video_name","vector_value"],dtype=object)
#    
#     with open(path+"output.pkl","wb") as f:
#         w = csv.writer(f)
#         for i, img in enumerate(vec.image_set):
# # =============================================================================
# #             df.loc[i,0] = img.split('\\')[-1]
# #             df.loc[i,1] = list(vec._vectorize(img))
# # =============================================================================
#             d[img.split('\\')[-1]] = vec._vectorize(img)
#             if i%10 == 0 and i!=0:
#               #  df.to_csv(path+"\\output.csv")
#                 pickle.dump(d,f)
#             print("Completed: "+str(i))
# =============================================================================


        
# =============================================================================
# def _construct_model(self):
#     
# # =============================================================================
# #         self._model.add(Conv2D(filters = 16, input_shape = (self.l,self.b,3), kernel_size= 5, strides = (2,3),activation='relu',kernel_initializer = "truncated_normal" ))
# #         self._model.add(Conv2D(filters = 32, kernel_size= 5, strides = (2,2),activation='relu',kernel_initializer = "truncated_normal" ))
# #         self._model.add(Conv2D(filters = 1, kernel_size= 5, strides = (2,3),activation='sigmoid' ,kernel_initializer = "truncated_normal",name=self.layer_name ))
# #         self._model.add(Conv2DTranspose(filters = 128, kernel_size= 7, strides = (2,3),activation='relu' ,kernel_initializer = "truncated_normal"))
# #         self._model.add(Conv2DTranspose(filters = 16, kernel_size= 5, strides = (2,2) ,activation='relu',kernel_initializer = "truncated_normal"))
# #         self._model.add(Conv2DTranspose(filters = 3, kernel_size= 5, strides = (2,3) ,activation='tanh',kernel_initializer = "truncated_normal"))
# #         
# # =============================================================================
# # =============================================================================
# #         self._model.add(Conv2D(filters = 16, input_shape = (self.l,self.b,3), kernel_size= 3, strides = (1,2),activation='relu',kernel_initializer = "random_normal" ))
# #         self._model.add(Conv2D(filters = 32, kernel_size= 3, strides = (1,1),activation='relu',kernel_initializer = "random_normal" ))
# #         self._model.add(Conv2D(filters = 64, kernel_size= 5, strides = (2,2),activation='relu',kernel_initializer = "random_normal" ))
# #         self._model.add(Conv2D(filters = 128, kernel_size= 5, strides = (2,2),activation='relu',kernel_initializer = "random_normal" ))
# #         self._model.add(Conv2D(filters = 1, kernel_size= 5, strides = (3,3),activation='relu' ,kernel_initializer = "random_normal",name="vector_layer"))
# #         self._model.add(Conv2DTranspose(filters = 128, kernel_size= 7, strides = (2,3),activation='relu' ,kernel_initializer = "truncated_normal"))
# #         self._model.add(Conv2DTranspose(filters = 64, kernel_size= 5, strides = (3,2) ,activation='relu',kernel_initializer = "truncated_normal"))
# #         self._model.add(Conv2DTranspose(filters = 16, kernel_size= 5, strides = (1,2) ,activation='relu',kernel_initializer = "truncated_normal"))
# #         self._model.add(Conv2DTranspose(filters = 3, kernel_size= 5, strides = (2,2) ,activation='sigmoid',kernel_initializer = "truncated_normal"))
# #                 
# #         sgd = optimizers.SGD(lr=0.0001, decay=0.01, momentum=0.8, nesterov=True)
# #         self._model.compile(optimizer=sgd,loss='mean_absolute_error',metrics=['accuracy'])
# #         self._model.summary()
# # =============================================================================
#     vgg16 = app.vgg16.VGG16()
#     chop_num = 4
#     
#     for num in range(chop_num):
#         vgg16.layers.pop()
#         
#   #  vgg16.layers.pop(0)
#     
#     for layer in vgg16.layers:
#         layer.trainable = False
#     
#     last_layer = vgg16.get_layer("block5_pool").output
#  #   first_layer = vgg16.get_layer("block1_conv1").output
#     
# # =============================================================================
# #         pre_layer1 = Input(shape=(640,480,3,),name="Input")
# #         pre_layer2 = Conv2D(filters=3,kernel_size=(194,34),strides=(2,2),activation='relu')(pre_layer1)
# #         mid_layer = vgg16(pre_layer2)
# # =============================================================================
#             
#     layer_1 = Conv2DTranspose(filters = 512, kernel_size= 4, strides=(1,1), padding= "valid", activation = "relu", name = "vector_layer",kernel_regularizer=regularizers.l2(0.01), kernel_initializer = "VarianceScaling")(last_layer)
#     layer_2 = Conv2DTranspose(filters = 256, kernel_size= 4, strides=(2,2), padding= "valid", activation = "relu",kernel_regularizer=regularizers.l2(0.01), kernel_initializer = "VarianceScaling")(layer_1)
#     layer_3 = Conv2DTranspose(filters = 128, kernel_size= 5, strides=(1,1), padding= "valid", activation = "relu",kernel_regularizer=regularizers.l2(0.01), kernel_initializer = "VarianceScaling")(layer_2)
#     layer_4 = Conv2DTranspose(filters = 64, kernel_size= 4, strides=(2,2), padding= "valid", activation = "relu",kernel_regularizer=regularizers.l2(0.01), kernel_initializer = "VarianceScaling")(layer_3)
#     layer_5 = Conv2DTranspose(filters = 32, kernel_size= 4, strides=(2,2), padding= "valid", activation = "relu",kernel_regularizer=regularizers.l2(0.01), kernel_initializer = "VarianceScaling")(layer_4)
#     layer_6 = Conv2DTranspose(filters = 16, kernel_size= 3, strides=(1,1), padding= "valid", activation = "relu",kernel_regularizer=regularizers.l2(0.01), kernel_initializer = "VarianceScaling")(layer_5)
#     layer_7 = Conv2DTranspose(filters = 3, kernel_size= 2, strides=(2,2), padding= "valid", activation = "tanh")(layer_6)
#     
# # =============================================================================
# #         model = Model(input = vgg16.input, output = layer_7)
# #         model.summary()
# # 
# # =============================================================================
#     
#     self._model = Model(input = vgg16.input, output = layer_7)
#     self._model.summary()
#     sgd = optimizers.SGD(lr=0.01)
#     self._model.compile(optimizer=sgd,loss='mean_squared_error',metrics=['accuracy'])
#     
#     
#     return True
#     
#     
# =============================================================================

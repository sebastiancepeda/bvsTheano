import numpy
from PIL import Image
from sklearn import preprocessing

def load_data(ImageShape, PatternShape, winSize, n_image = 21):
    print('Reading data. ')
    #
    x_image 	   = Image.open('../DRIVE/training/images/'+str(n_image)+'_training.tif','r')    
    x_image     = numpy.fromstring(x_image.tobytes(), dtype='uint8', count=-1, sep='')
    x_image     = numpy.reshape(x_image,ImageShape,'A')
    #
    t_image     = Image.open('../DRIVE/training/1st_manual/'+str(n_image)+'_manual1.gif','r')
    t_image     = numpy.fromstring(t_image.tobytes(), dtype='uint8', count=-1, sep='')
    t_image     = numpy.reshape(t_image,PatternShape,'A')
    #
    mask_image     = Image.open('../DRIVE/training/mask/'+str(n_image)+'_training_mask.gif','r')
    mask_image     = numpy.fromstring(mask_image.tobytes(), dtype='uint8', count=-1, sep='')
    mask_image     = numpy.reshape(mask_image,PatternShape,'A')
    #
    x  = sliding_window(x_image, stepSize=1, w=winSize, dim=ImageShape[2],output=0)
    x = x.reshape(x.shape[0], numpy.floor(x.size/x.shape[0]).astype(int))
    #
    t  = sliding_window(t_image, stepSize=1, w=winSize, dim=1,output=1)
    t = t[:,0]
    #
    mask  = sliding_window(mask_image, stepSize=1, w=winSize, dim=1,output=1)
    mask = mask[:,0]
    print('Scaling data. ')
    x = preprocessing.scale(x)
    #min_max_scaler = preprocessing.MinMaxScaler()
    #x = min_max_scaler.fit_transform(x)
    return x, t,  mask

'''
Method to balance the training set between the classes  
'''
def balance(x,  t):
    nv  = t.sum()
    nf   = t.size - nv
    t2 = numpy.zeros((numpy.floor(nv*2*beta), 1))
    x2 = numpy.zeros((numpy.floor(nv*2*beta), winSize[0],  winSize[1],  ImageShape[2]))
    c = 0
    for i in numpy.arange(t.size):
        if (c == (t2.size-1)):
            x2[c] = x[x.shape[0]-1]
            t2[c]  = t[t.shape[0]-1]
            print('t2.size')
            print(t2.size)
            return x2,  t2
        if(t[i]==1):
            if(numpy.random.rand() < beta*nf/(nv+nf)):
                x2[c] = x[i]
                t2[c] = 1
                c += 1
        if(t[i]==0):
            if(numpy.random.rand() < beta*nv/(nv+nf)):
                x2[c] = x[i]
                t2[c]  = 0
                c += 1
    print('t2.size')
    print(t2.size)
    return x2,  t2

'''
if output == 0, for every pixel of the image, a list of pixels of a window around it is returned. 
if output == 1, for every pixel of the image, 1 is returned if the pixel corresponds to a blood vessel, 0 otherwise. 
'''
def sliding_window(image, stepSize, w, dim,output):
    n1 = image.shape[0]
    n2 = image.shape[1]
    diff = (w[0]-1)/2
    valid_windows = n1*n2-diff*2*(n1+n2)+4*diff*diff
    if(output == 1):
        value = numpy.zeros((valid_windows,1))
        mean_sample = numpy.zeros((1,1))
    else:
        value = numpy.zeros((valid_windows,w[0],w[1],dim))
        mean_sample = numpy.zeros((w[0],w[1],dim))
    c = 0
    # slide a window across the image
    for x in xrange(w[0]//2, image.shape[0]-w[0]//2, stepSize):
        for y in xrange(w[1]//2, image.shape[1]-w[1]//2, stepSize):
            # If it is the groundtruth that is being streamed
            if(output == 1):
                sample = image[x,y]
                if(sample >= 127):
                    sample = 1
                else:
                    sample = 0
                value[c,] = sample
            else:
                window = image[(x-w[0]//2):(x+w[0]//2+1), (y-w[1]//2):(y+w[1]//2+1)]
                if window.shape[0] != w[0] or window.shape[1] != w[1]:
                    continue
                sample = window
                value[c,] = sample
            c += 1
            mean_sample += sample/c
    return value

def sliding_window2(image, stepSize, w, dim):
    n1 = image.shape[0]
    n2 = image.shape[1]
    diff = (w[0]-1)/2
    valid_windows = n1*n2-diff*2*(n1+n2)+4*diff*diff
    value = numpy.zeros((valid_windows,1))
    c = 0
    # slide a window across the image
    for x in xrange(w[0]//2, image.shape[0]-w[0]//2, stepSize):
        for y in xrange(w[1]//2, image.shape[1]-w[1]//2, stepSize):
            # If it is the groundtruth that is being streamed
            sample = image[x,y]
            value[c,] = sample
            c += 1
    return value

def reconstruct_image(y_preds,w, PatternShape, alpha):
    a = 0
    output_image = numpy.zeros((PatternShape[0],PatternShape[1]))
    for x in xrange(w[0]//2, PatternShape[0]-w[0]//2, 1):
        for y in xrange(w[1]//2, PatternShape[1]-w[1]//2, 1):
            if(y_preds[a][0] > y_preds[a][1]*alpha):
                output_image[x][y] = 0
            else:
                output_image[x][y] = 1
            a += 1
    return output_image
    
def reconstruct_image_2(e_preds,w, PatternShape):
    a = 0
    output_image = numpy.zeros((PatternShape[0],PatternShape[1]))
    for x in xrange(w[0]//2, PatternShape[0]-w[0]//2, 1):
        for y in xrange(w[1]//2, PatternShape[1]-w[1]//2, 1):
            output_image[x][y] = e_preds[a][0]
            a += 1
    return output_image
    
def reconstruct_image_3(e_preds,w,PatternShape):
    a = 0
    output_image = numpy.zeros((PatternShape[0],PatternShape[1]))
    for x in xrange(w[0]//2, PatternShape[0]-w[0]//2, 1):
        for y in xrange(w[1]//2, PatternShape[1]-w[1]//2, 1):
            output_image[x][y] = e_preds[a]
            a += 1
    return output_image
    
def get_error_image(output_image, t_image,  mask_image):
    error_image = numpy.zeros((output_image.shape[0], output_image.shape[1], 3))
    background = (1-mask_image)
    tp_image    = output_image*t_image*mask_image
    tn_image    = (1-output_image)*(1-t_image)*mask_image
    fp_image    = output_image*(1-t_image)*mask_image
    fn_image    = (1-output_image)*t_image*mask_image
    r = background+fp_image
    g = background+tp_image
    b = background+fn_image
    error_image[:, :, 0] = r
    error_image[:, :, 1] = g
    error_image[:, :, 2] = b
    accuracy = (tp_image.sum()+tn_image.sum())/mask_image.sum()
    return error_image,  accuracy

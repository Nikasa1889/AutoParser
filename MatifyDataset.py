import os
import sys
import urllib
import random
from MatifyAPI import MatifyAPI
from requests import Session
import io
import tensorflow as tf
import math
#sys.path.append(os.path.abspath("/notebooks/AutoParser/squeezenet/models/slim/"))
import dataset_utils
import json
slim = tf.contrib.slim

class ImageReader(object):
    """Helper class that provides TensorFlow image coding utilities."""

    def __init__(self):
        # Initializes function that decodes RGB JPEG data.
        self._decode_jpeg_data = tf.placeholder(dtype=tf.string)
        self._decode_jpeg = tf.image.decode_jpeg(self._decode_jpeg_data, channels=3)

    def read_image_dims(self, sess, image_data):
        image = self.decode_jpeg(sess, image_data)
        return image.shape[0], image.shape[1]

    def decode_jpeg(self, sess, image_data):
        image = sess.run(self._decode_jpeg,
                     feed_dict={self._decode_jpeg_data: image_data})
        assert len(image.shape) == 3
        assert image.shape[2] == 3
        return image
    
class MatifyDataset:
    '''Class to download and convert all product images from Matify database
        Options:
         datasetDir: string, directory where all the images are stored. A subdirectory is created for each category of product, 
                     where all images belong to that category are stored 
         leastExamples: int, only category with more than leastExamples is downloaded
         nShards:       int, the number of tfrecords files that used to store the dataset
         nValidations:  int, number of validation examples
         nTrainings     int, number of training examples. 
                             If None, try to infer this number from total - nValidations. 
                             total is number of images
         randomSeed:    int, make repeatable splitting between training and validation set
         verbose:       bool, printing the process or not'''
    def __init__ (self, datasetDir = 'Matify/MatifyDataset/', leastExamples = 15, nShards = 1, 
                  nValidations = 20, nTrains = None, randomSeed = 0, verbose = False):
        self.leastExamples = leastExamples
        self.datasetDir = datasetDir
        self.nShards = nShards
        self.randomSeed = randomSeed
        self.nValidations = nValidations
        self.nTrains      = None
        self.verbose = verbose
        
        ##labels_to_names and nClasses will be infered automatically when convertToTfRecord or getSplit is called
        self.labels_to_names = None
        self.nClasses = None
        
        self.SPLITS_NAMES = ['train', 'validation']
        self._FILE_PATTERN = 'matify_%s_*.tfrecord'
        self._NUM_CLASSES = None
        self._ITEMS_TO_DESCRIPTIONS = {
            'image': 'A color image of varying size.',
            'label': 'A single integer',
        }

    def _download_all_images (self, productWithImages):
        for categoryName, products in productWithImages:
            categoryPath =  os.path.join(self.datasetDir,
                                      categoryName)
            #if len(products) >= self.leastExamples:
            if not os.path.exists(categoryPath):
                os.makedirs(categoryPath)
            for product in products:
                if product["image"]:
                    urllib.urlretrieve(product["image"], os.path.join(categoryPath, str(product["id"]) + ".jpg"))
                    with open(os.path.join(categoryPath, str(product["id"]) + ".json"), 'w') as outfile:
                        json.dump(product, outfile)

    def _get_filenames_and_classes(self):
        """Returns a list of filenames and inferred class names.
        Args:
        dataset_dir: A directory containing a set of subdirectories representing
          class names. Each subdirectory should contain PNG or JPG encoded images.
        Returns:
        A list of image file paths, relative to `dataset_dir` and the list of
        subdirectories, representing class names.
        """
        root = self.datasetDir
        directories = []
        class_names = []
        for filename in os.listdir(root):
            path = os.path.join(root, filename)
            if os.path.isdir(path):
                directories.append(path)
                class_names.append(filename)

        photo_filenames = []
        for directory in directories:
            for filename in os.listdir(directory):
                path = os.path.join(directory, filename)
                photo_filenames.append(path)

        return photo_filenames, sorted(class_names)

    def _get_dataset_filename(self, split_name, shard_id):
        output_filename = 'matify_%s_%05d-of-%05d.tfrecord' % (
            split_name, shard_id, self.nShards)
        return os.path.join(self.datasetDir, output_filename)

    def _convert_dataset(self, split_name, filenames, class_names_to_ids):
        """Converts the given filenames to a TFRecord dataset.
        Args:
        split_name: The name of the dataset, either 'train' or 'validation'.
        filenames: A list of absolute paths to png or jpg images.
        class_names_to_ids: A dictionary from class names (strings) to ids
          (integers).
        dataset_dir: The directory where the converted datasets are stored.
        """
        assert split_name in self.SPLITS_NAMES

        num_per_shard = int(math.ceil(len(filenames) / float(self.nShards)))

        with tf.Graph().as_default():
            image_reader = ImageReader()

            with tf.Session('') as sess:

                for shard_id in range(self.nShards):
                    output_filename = self._get_dataset_filename(split_name, shard_id)

                    with tf.python_io.TFRecordWriter(output_filename) as tfrecord_writer:
                        start_ndx = shard_id * num_per_shard
                        end_ndx = min((shard_id+1) * num_per_shard, len(filenames))
                        for i in range(start_ndx, end_ndx):
                            sys.stdout.write('\r>> Converting image %d/%d shard %d' % (i+1, len(filenames), shard_id))
                            sys.stdout.flush()

                            # Read the filename:
                            image_data = tf.gfile.FastGFile(filenames[i], 'r').read()
                            height, width = image_reader.read_image_dims(sess, image_data)

                            class_name = os.path.basename(os.path.dirname(filenames[i]))
                            class_id = class_names_to_ids[class_name]

                            example = dataset_utils.image_to_tfexample(
                                image_data, 'jpg', height, width, class_id)
                            tfrecord_writer.write(example.SerializeToString())

        sys.stdout.write('\n')
        sys.stdout.flush()
        
    def download (self):
        matifyAPI = MatifyAPI(verbose=False)
        categories = matifyAPI.getCategories()
        #Request products from all sub category
        allProducts = []
        for categoryId, categoryName, subCategories in categories:
            #products = matifyAPI.getProducts (categoryId, categoryName)
            #allProducts.append([categoryName, products])
            for subCategoryID, subCategoryName, _ in subCategories:
                try:
                    supermarkets = matifyAPI.getProducts (subCategoryID, subCategoryName)
                    print subCategoryName
                    for supermarket in supermarkets:
                        allProducts.append([subCategoryName, supermarket["products"]])
                except Exception, e:
                    print e
                    continue
        #productWithImages = matifyAPI.filterProductWithImage (allProducts, verbose=self.verbose)

        #Download all images
        self._download_all_images (allProducts)

    def convertToTfrecord (self, nValidations = None):
        if not nValidations:
            nValidations = self.nValidations
        self.nValidations = nValidations
        #convert to Tfrecords
        photo_filenames, class_names = self._get_filenames_and_classes()
        class_names_to_ids = dict(zip(class_names, range(len(class_names))))

        # Divide into train and test:
        random.seed(self.randomSeed)
        random.shuffle(photo_filenames)
        training_filenames = photo_filenames[nValidations:]
        validation_filenames = photo_filenames[:nValidations]
        self.nTrains = len(photo_filenames) - nValidations
        
        # First, convert the training and validation sets.
        self._convert_dataset('train', training_filenames, class_names_to_ids)
        self._convert_dataset('validation', validation_filenames, class_names_to_ids)

        # Finally, write the labels file:
        labels_to_class_names = dict(zip(range(len(class_names)), class_names))
        dataset_utils.write_label_file(labels_to_class_names, self.datasetDir)
        self.labels_to_names = labels_to_class_names
        self.nClasses = len(labels_to_class_names)
        print('\nFinished converting the Matify dataset!')
    
    def getSplit (self, split_name, nValidations = None):
        if not nValidations:
            if not self.nValidations:
                raise ValueError("nValidations is not known");
            else:
                nValidations = self.nValidations
                
        if not self.nTrains:
            photo_filenames, _ = self._get_filenames_and_classes()
            self.nTrains = len(photo_filenames) - self.nValidations
            
        if split_name not in self.SPLITS_NAMES:
            raise ValueError('split name %s was not recognized.' % split_name)
        file_pattern = self._FILE_PATTERN
        file_pattern = os.path.join(self.datasetDir, file_pattern % split_name)

        reader = tf.TFRecordReader

        keys_to_features = {
              'image/encoded': tf.FixedLenFeature((), tf.string, default_value=''),
              'image/format': tf.FixedLenFeature((), tf.string, default_value='jpg'),
              'image/class/label': tf.FixedLenFeature(
                  [], tf.int64, default_value=tf.zeros([], dtype=tf.int64)),
          }

        items_to_handlers = {
          'image': slim.tfexample_decoder.Image(),
          'label': slim.tfexample_decoder.Tensor('image/class/label'),
        }

        decoder = slim.tfexample_decoder.TFExampleDecoder(keys_to_features, items_to_handlers)

        labels_to_names = None
        if dataset_utils.has_labels(self.datasetDir):
            labels_to_names = dataset_utils.read_label_file(self.datasetDir)
            self.labels_to_names = labels_to_names
            self.nClasses = len(labels_to_names)
        else:
            raise ValueError("Can't find label file in the data directory: " + self.datasetDir);
            
        return slim.dataset.Dataset(
          data_sources=file_pattern,
          reader=reader,
          decoder=decoder,
          num_samples=self.nTrains, 
          items_to_descriptions=self._ITEMS_TO_DESCRIPTIONS,
          num_classes=len(labels_to_names),
          labels_to_names=labels_to_names)
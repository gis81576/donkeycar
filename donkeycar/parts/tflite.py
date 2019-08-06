import tensorflow as tf

def keras_model_to_tflite(in_filename, out_filename):
    converter = tf.lite.TFLiteConverter.from_keras_model_file(in_filename)
    tflite_model = converter.convert()
    open(out_filename, "wb").write(tflite_model)

def keras_session_to_tflite(model, out_filename):
    inputs = model.inputs
    outputs = model.outputs
    with tf.keras.backend.get_session() as sess:        
        converter = tf.lite.TFLiteConverter.from_session(sess, inputs, outputs)
        tflite_model = converter.convert()
        open(out_filename, "wb").write(tflite_model)


class TFLitePilot(object):
    '''
    Base class for TFlite models that will provide steering and throttle to guide a car.
    '''
    def __init__(self):
        self.model = None
 
    
    def load(self, model_path):
        # Load TFLite model and allocate tensors.
        self.interpreter = tf.lite.Interpreter(model_path=model_path)
        self.interpreter.allocate_tensors()

        # Get input and output tensors.
        self.input_details = self.interpreter.get_input_details()
        self.output_details = self.interpreter.get_output_details()

        # Get Input shape
        self.input_shape = self.input_details[0]['shape']

    
    def run(self, image):
        input_data = image.reshape(self.input_shape).astype('float32') 

        self.interpreter.set_tensor(self.input_details[0]['index'], input_data)
        self.interpreter.invoke()

        steering = 0.0
        throttle = 0.0
        outputs = []

        for tensor in self.output_details:
            output_data = self.interpreter.get_tensor(tensor['index'])
            outputs.append(output_data[0][0])

        if len(outputs) > 1:
            steering = outputs[0]
            throttle = outputs[1]

        return steering, throttle



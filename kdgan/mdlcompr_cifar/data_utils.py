import cifar10_utils

import tensorflow as tf
import math

class CIFAR(object):
  def __init__(self, flags):
    cifar10_utils.maybe_download_and_extract()
    with tf.device('/cpu:0'):
      self.tn_image_ts, self.tn_label_ts = cifar10_utils.distorted_inputs()
      self.vd_image_ts, self.vd_label_ts = cifar10_utils.inputs(eval_data=True)
    self.vd_num_batch = int(math.ceil(flags.valid_size / flags.batch_size))

  def next_batch(self, sess):
    tn_image_np, tn_label_np = sess.run([self.tn_image_ts, self.tn_label_ts])
    return tn_image_np, tn_label_np

  def evaluate(self, sess, vd_std):
    acc_list = []
    for vd_batch in range(self.vd_num_batch):
      vd_image_np, vd_label_np = sess.run([self.vd_image_ts, self.vd_label_ts])
      feed_dict = {vd_std.image_ph:vd_image_np, vd_std.hard_label_ph:vd_label_np}
      acc = sess.run(vd_std.accuracy, feed_dict=feed_dict)
      acc_list.append(acc)
    acc = sum(acc_list) / len(acc_list)
    return acc













from kdgan import config
from kdgan import metric
from kdgan import utils
from flags import flags
from tch_model import TCH

import os
import time

import numpy as np
import tensorflow as tf

from os import path
from tensorflow.contrib import slim

tn_size = utils.get_tn_size(flags.dataset)
vd_size = utils.get_vd_size(flags.dataset)
print('#tn_data=%d #vd_data=%d' % (tn_size, vd_size))
tn_num_batch = int(flags.num_epoch * tn_size / flags.batch_size)
print('#batch=%d' % (tn_num_batch))
eval_interval = int(tn_size / flags.batch_size)

tch_t = TCH(flags, is_training=True)
scope = tf.get_variable_scope()
scope.reuse_variables()
tch_v = TCH(flags, is_training=False)

tf.summary.scalar(tch_t.learning_rate.name, tch_t.learning_rate)
tf.summary.scalar(tch_t.pre_loss.name, tch_t.pre_loss)
summary_op = tf.summary.merge_all()
init_op = tf.global_variables_initializer()

for variable in tf.trainable_variables():
  num_params = 1
  for dim in variable.shape:
    num_params *= dim.value
  print('%-50s (%d params)' % (variable.name, num_params))

tn_data_sources = utils.get_data_sources(flags, is_training=True, single_source=True)
print('#tfrecord=%d' % (len(tn_data_sources)))

tn_ts_list = utils.decode_tfrecord(flags, tn_data_sources, shuffle=True)
tn_bt_list = utils.generate_batch(tn_ts_list, flags.batch_size)
tn_user_bt, tn_image_bt, tn_text_bt, tn_label_bt, _ = tn_bt_list

vd_image_np, vd_text_np, vd_label_np, _ = utils.get_valid_data(flags)

def main(_):
  bst_hit = -np.inf
  writer = tf.summary.FileWriter(config.logs_dir, graph=tf.get_default_graph())
  with tf.train.MonitoredTrainingSession() as sess:
    sess.run(init_op)
    start = time.time()
    for batch_t in range(tn_num_batch):
      tn_image_np, tn_text_np, tn_label_np = sess.run([tn_image_bt, tn_text_bt, tn_label_bt])
      feed_dict = {
        tch_t.image_ph:tn_image_np,
        tch_t.text_ph:tn_text_np,
        tch_t.hard_label_ph:tn_label_np
      }
      _, summary = sess.run([tch_t.pre_update, summary_op], feed_dict=feed_dict)
      writer.add_summary(summary, batch_t)

      if (batch_t + 1) % eval_interval != 0:
          continue
      feed_dict = {
        tch_v.image_ph:vd_image_np,
        tch_v.text_ph:vd_text_np,
      }
      logit_np_v = sess.run(tch_v.logits, feed_dict=feed_dict)
      hit = metric.compute_hit(logit_np_v, vd_label_np, flags.cutoff)

      bst_hit = max(hit, bst_hit)
      tot_time = time.time() - start
      global_step = sess.run(tch_t.global_step)
      avg_time = (tot_time / global_step) * (tn_size / flags.batch_size)
      print('#%08d curhit=%.4f curbst=%.4f tot=%.0fs avg=%.2fs/epoch' % 
          (global_step, hit, bst_hit, tot_time, avg_time))

      if hit < bst_hit:
        continue
      tch_t.saver.save(utils.get_session(sess), flags.tch_model_ckpt)
  print('bsthit=%.4f' % (bst_hit))

if __name__ == '__main__':
  tf.app.run()
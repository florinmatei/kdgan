kdgan_dir=$HOME/Projects/kdgan/kdgan
checkpoint_dir=$kdgan_dir/checkpoints


python train_gan.py \
  --dis_checkpoint_dir=$checkpoint_dir/mdlcompr_mnist_dis \
  --gen_checkpoint_dir=$checkpoint_dir/mdlcompr_mnist_gen \
  --dataset_dir=$HOME/Projects/data/mnist \
  --num_epoch=100 \
  --num_dis_epoch=20 \
  --num_gen_epoch=10
exit


python pretrain_dis.py \
  --dis_checkpoint_dir=$checkpoint_dir/mdlcompr_mnist_dis \
  --dis_save_path=$checkpoint_dir/mdlcompr_mnist_dis/model \
  --dataset_dir=$HOME/Projects/data/mnist \
  --num_epoch=200
# target=0.9854
# bstacc=0.9862 # no dropout no l2
# bstacc=0.9884 # wt dropout wt l2
exit


python pretrain_gen.py \
  --gen_checkpoint_dir=$checkpoint_dir/mdlcompr_mnist_gen \
  --gen_save_path=$checkpoint_dir/mdlcompr_mnist_gen/model \
  --dataset_dir=$HOME/Projects/data/mnist \
  --num_epoch=200
# target=0.9854
# bstacc=0.9862 # no dropout no l2
# bstacc=0.9884 # wt dropout wt l2
exit


for tch_keep_prob in 0.95 0.90 0.85 0.80 0.75
do
  for tch_weight_decay in 0.0001 0.00005 0.00001
  do
    python pretrain_tch.py \
      --tch_checkpoint_dir=$checkpoint_dir/mdlcompr_mnist_tch \
      --tch_save_path=$checkpoint_dir/mdlcompr_mnist_tch/model \
      --dataset_dir=$HOME/Projects/data/mnist \
      --tch_keep_prob=$tch_keep_prob \
      --tch_weight_decay=$tch_weight_decay \
      --num_epoch=200
    # target=0.9932
    # bstacc=0.9951
  done
done
exit


python train_kd.py \
  --gen_checkpoint_dir=$checkpoint_dir/mdlcompr_mnist_gen \
  --tch_checkpoint_dir=$checkpoint_dir/mdlcompr_mnist_tch \
  --dataset_dir=$HOME/Projects/data/mnist \
  --tch_model_name=lenet \
  --preprocessing_name='lenet'
exit


python chk_model.py \
  --dataset_dir=$HOME/Projects/data/mnist \
  --model_name=lenet \
  --preprocessing_name='lenet'
exit



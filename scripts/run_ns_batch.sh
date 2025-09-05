for i in {1..8}; do
  # training
  train_cmd="ns-train nerfacto \
      --max-num-iterations 30000 \
      --steps-per-eval-image 10000 \
      --vis wandb \
      --pipeline.model.camera-optimizer.mode off \
      nerfstudio-data --data /home/docker_dev/oxford_spires_dataset/data/saplings_nerf/2025-08-14-wytham/sapling-0${i}/raw/ \
      --orientation_method none \
      --center_method none"
  echo -e "\033[1;36mRunning:\033[0m $train_cmd"
  eval $train_cmd

  # export point cloud
  latest_run=$(ls -td /home/docker_dev/oxford_spires_dataset/outputs/unnamed/nerfacto/* | head -1)
  echo -e "\033[1;36mLatest run directory:\033[0m $latest_run"
  export_cmd="ns-export pointcloud \
      --load-config ${latest_run}/config.yml \
      --output-dir /home/docker_dev/oxford_spires_dataset/ns_export \
      --num-points 5000000 \
      --remove-outliers True \
      --normal-method open3d \
      --save-world-frame True \
      --obb_center 0. 0. 0. \
      --obb_rotation 0. 0. 0. \
      --obb_scale 10. 10. 10."
  echo -e "\033[1;36mRunning:\033[0m $export_cmd"
  eval $export_cmd  

  # rename the exported point cloud
  mv /home/docker_dev/oxford_spires_dataset/ns_export/point_cloud.ply /home/docker_dev/oxford_spires_dataset/ns_export/sapling-0${i}.ply
done


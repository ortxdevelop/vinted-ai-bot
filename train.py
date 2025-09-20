from fastai.vision.all import *
from pathlib import Path

def get_dataloaders(path):
    dblock = DataBlock(
        blocks=(ImageBlock, CategoryBlock),
        get_items=get_image_files,
        splitter=RandomSplitter(valid_pct=0.2, seed=42),
        get_y=parent_label,
        item_tfms=Resize(256),
        batch_tfms=[
            *aug_transforms(
                size=224,
                max_rotate=5,
                max_zoom=1.05,
                max_lighting=0.1,
                max_warp=0.1,
                p_affine=0.4,
                p_lighting=0.4
            ),
            Normalize.from_stats(*imagenet_stats)
        ]
    )
    return dblock.dataloaders(path, bs=8, num_workers=0)

def main():
    path = Path('dataset')  # structure: dataset/big_pony/*.jpg, dataset/other/*.jpg
    dls = get_dataloaders(path)

    print(f'Classes: {dls.vocab}')
    print(f'Training: {len(dls.train_ds)}, Validate: {len(dls.valid_ds)}')

    learn = vision_learner(
        dls,
        resnet34,
        metrics=accuracy,
        loss_func=LabelSmoothingCrossEntropy(),
        pretrained=True
    )

    # 1.Learning only head
    learn.fine_tune(3, base_lr=3e-3)

    # 2. Unfreaze and learning whole chain
    learn.unfreeze()
    learn.fit_one_cycle(15, lr_max=slice(1e-5, 1e-3), wd=0.01)

    # 3. Quality rate with TTA
    print("Rate with TTA...")
    preds, targs = learn.tta()
    acc = accuracy(preds, targs)
    print(f"Final accuracy (TTA): {acc.item() * 100:.2f}%")

    # 4. Saving the model
    learn.export('big_pony_model.pkl')
    print("Model saved")

    # 5. Error visualization
    interp = ClassificationInterpretation.from_learner(learn)
    interp.plot_confusion_matrix()
    interp.plot_top_losses(6, nrows=2)

if __name__ == '__main__':
    main()

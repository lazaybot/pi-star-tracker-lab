# Optical calibration and validation

## Intrinsic calibration

Before real-sky attitude estimation, determine:

- focal length in pixels for both image axes;
- optical center/principal point;
- radial and tangential lens distortion;
- stable manual-focus position;
- sensor orientation relative to the enclosure.

Use at least 20 sharp checkerboard images covering the center, edges, corners,
and multiple rotations. Reject blurred or nearly identical views. Save the
calibration result with the camera serial number, lens, focus setting, image
resolution, and date.

## Sensor calibration

Capture dark frames to locate hot pixels and measure background variation.
Median-combine multiple frames rather than trusting one exposure. A fixed hot
pixel can resemble a star but does not move with the sky; the centroid pipeline
already rejects isolated one-pixel detections, but a dark-frame mask is still
required for real data.

## Accuracy experiment

For each test field, report:

- stars detected and matched;
- rejected centroids;
- acquisition time;
- attitude residual and repeatability;
- exposure and analog gain;
- ambient temperature and visible glare;
- catalog and calibration versions.

Compare the solution with an independently calculated sky pointing. Synthetic
ground truth is useful for software testing but cannot substitute for this
experiment.

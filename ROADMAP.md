# Engineering roadmap

## Complete in version 0.1

- Pinhole camera projection and inverse projection
- Synthetic unit-vector catalog
- Configurable centroid noise and star dropout
- SVD solution to Wahba's attitude-determination problem
- Quaternion output and angular-error measurement
- Automated numerical tests
- Rotation-invariant triangle catalog
- Lost-in-space hypothesis search and false-star rejection
- Gaussian sensor-image simulation, read noise, and hot pixels
- Connected-component and weighted-centroid extraction
- Image-to-attitude integration test
- Monte Carlo noise/dropout benchmark

## Next: image processing

- Add Poisson shot noise and spatially varying background glow
- Calibrate focal length, principal point, and lens distortion
- Compare simulated centroids with extracted centroids

## Next: real-catalog identification

- Build a licensed bright-star catalog from Hipparcos data
- Tune triangle/pyramid patterns against real catalog density
- Reject ambiguous patterns using magnitude and image-quality evidence
- Add acquisition time and false-solution benchmarks

## Next: hardware validation

- Raspberry Pi 5 and HQ Camera with a fixed-focus C/CS lens
- Rigid, light-shielded enclosure and tripod mount
- Dark-frame and hot-pixel calibration
- Real night-sky captures at multiple exposures
- Repeatability, angular-error, glare, and motion-blur tests

No flight-readiness claim should be made from terrestrial testing alone.

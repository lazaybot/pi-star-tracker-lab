# Pi Star Tracker Lab

A Raspberry Pi-oriented spacecraft attitude-determination laboratory with a
calibrated synthetic star-field generator and testable three-axis estimator.

NASA describes a star tracker as a camera and computer that compares observed
star patterns with an onboard catalog to determine spacecraft orientation. This
project implements both associated-star tracking and a synthetic lost-in-space
acquisition mode. Acquisition indexes rotation-invariant star triangles,
searches candidate correspondences, scores full-catalog rotation hypotheses,
and rejects unmatched observations.

## Run the laboratory

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e .
star-tracker-lab --yaw 8 --pitch -5 --roll 3 --noise-px 0.5 --dropout 0.15
star-tracker-lab --mode lost-in-space --yaw 18 --pitch -9 --roll 6 --noise-px 0.15
python -m unittest discover -s tests -v
```

The JSON result reports visible associated stars, the estimated quaternion, and
the angular attitude error.

Run a repeatable Monte Carlo sweep:

```bash
star-tracker-benchmark --trials 20
```

The project also includes Gaussian point-spread rendering, read noise, hot
pixels, connected-component detection, intensity-weighted centroids, and an
end-to-end synthetic image-to-attitude test.

## Claim boundary

This is a tested synthetic tracker and triangle-pattern acquisition laboratory.
It does not yet use a real Hipparcos-derived catalog and has not been validated
with a Raspberry Pi camera under the night sky. Synthetic success is not proof
of flight readiness. Planned engineering phases are in [ROADMAP.md](ROADMAP.md).

## Why it is aerospace engineering

Attitude knowledge is required to point spacecraft instruments, antennas, and
solar arrays. NASA's Small Spacecraft technology review explains that star
trackers estimate absolute three-axis attitude by matching digital imagery to a
star catalog, while glare, angular rate, field of view, and processing limits
affect performance.

References:

- [NASA Small Spacecraft GNC and star trackers](https://www.nasa.gov/smallsat-institute/sst-soa/guidance-navigation-and-control/)
- [NASA COTS Star Tracker](https://github.com/nasa/COTS-Star-Tracker)
- [Raspberry Pi camera hardware](https://www.raspberrypi.com/documentation/accessories/camera.html)

Hardware work: [parts](PARTS.md), [assembly](HARDWARE_SETUP.md), and
[optical calibration](CALIBRATION.md).

## License

BSD-3-Clause. This project is independent and does not redistribute NASA COTS
Star Tracker source code.

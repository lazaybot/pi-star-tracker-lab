# Raspberry Pi real-sky setup

This phase is for terrestrial engineering validation, not flight qualification.

## Mechanical assembly

1. Mount the Raspberry Pi HQ Camera and manual-focus lens to a rigid plate.
2. Add a matte-black cylindrical light baffle that does not enter the lens field
   of view.
3. Use the correct 15-pin-to-22-pin cable for Raspberry Pi 5 and provide strain
   relief without sharply folding the cable.
4. Mount the plate to a tripod. Hand-held images are unsuitable for measuring
   star-centroid or attitude repeatability.
5. Keep the optical assembly away from the Pi's heat exhaust and bright LEDs.

## Software preparation

```bash
sudo apt update
sudo apt install -y python3-picamera2 python3-opencv python3-venv
rpicam-hello
python3 -m venv --system-site-packages .venv
source .venv/bin/activate
python -m pip install -e .
python -m unittest discover -s tests -v
```

## Capture sequence

1. Set manual focus at infinity and disable autofocus changes.
2. Capture dark frames with the lens cap installed at every intended exposure.
3. Start with one-second RAW captures, then increase exposure only as needed.
4. Avoid the Moon, streetlights, clouds, and direct horizon glow.
5. Record exposure, gain, temperature, lens, timestamp, and mount orientation
   alongside every frame.
6. Never use one successful image as the accuracy result; repeat across multiple
   fields, nights, temperatures, and camera orientations.

Raspberry Pi documents that the HQ Camera accepts interchangeable C/CS lenses
and supports exposures substantially longer than phone-style camera modules.

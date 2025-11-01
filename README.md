[![Python package](https://github.com/kilroyd/powerwall_control/actions/workflows/python-package.yml/badge.svg)](https://github.com/kilroyd/powerwall_control/actions/workflows/python-package.yml)
[![Hassfest](https://github.com/kilroyd/powerwall_control/actions/workflows/hassfest.yaml/badge.svg)](https://github.com/kilroyd/powerwall_control/actions/workflows/hassfest.yaml)
[![Hacs](https://github.com/kilroyd/powerwall_control/actions/workflows/validate.yaml/badge.svg)](https://github.com/kilroyd/powerwall_control/actions/workflows/validate.yaml)

# Overview

The [Tesla Powerwall](https://www.tesla.com/powerwall) [Home Assistant
integration](https://www.home-assistant.io/integrations/powerwall/)
allows you to get Powerwall status. However it doesn't provide any
control over the Powerwall.

This integration uses the [Netzero App](https://www.netzero.energy)
[Developer API](https://docs.netzero.energy/docs/tesla/API) to control
the Powerwall. Use of the Developer API is free. The Netzero App
supports a number of features (automation, monitorring, diagnostics)
via subscription - if you have a Powerwall and/or Tesla consider
subscribing. Note that the Netzero App, and by extension the Developer
API, are only for non-commercial use.

The benefit of this setup is that you just need an API Token and
System ID from Netzero - there's no need to set up an application or
host a public key.

# Installing

This integration is at an early stage of development. It must be
installed from source. HACS is not aware of this integration yet, but
you should be able to import it as a [custom
repository](https://www.hacs.xyz/docs/faq/custom_repositories/).

## Manual installation

Download the latest
[release](https://github.com/kilroyd/powerwall_control/releases) from
Github.

Copy the subdirectory custom_components/powerwall_control to your Home
Assistant server's &lt;config&gt;/custom_components directory.

    cp -r powerwall_control/custom_components/powerwall_control \
          $HOME_ASSIST_CONFIG_DIR/custom_components/.

## HACS custom repository

With [HACS installed](https://www.hacs.xyz/docs/use/download/download/)

* Click on the 3 dots in the top right corner.

* Select "Custom repositories"

* Set the URL to https://github.com/kilroyd/powerwall_control

* Set the type to "Integration".

* Click the "ADD" button.

# Setup the Powerwall Control integration

* Download the Netzero App onto your phone from the Apple store or the
  Google Play Store as appropriate.

* Sign into the Netzero App with your Tesla username and password.

* Separately sign into your Tesla account (not in the Tesla App), and
  approve access for the Netzero App. Netzero will appear under the
  Manage Access page of the app as a third party.

* The free Netzero Basic subscription is sufficient.

* In the Netzero App, go to Settings->Developer API.

* Take a note of the API Token and System ID.

* In Home Assistant navigate to the Settings->Devices and Services
  tab.

* Select "Add integration".

* Search for "Tesla Powerwall Control", and select it.

* Paste the API Token and System ID into the relevant text boxes and
  press Submit.

At this point you should see that a device has been added with 4 entities.

# Supported entities

* [Battery backup reserve
  (%)](https://www.tesla.com/en_gb/support/energy/powerwall/mobile-app/backup-reserve). This
  is the level of charge that the Powerwall reserves, to be used in
  the event of a power cut. See footnote[^1].

* Operational mode. Can be one of:

  - Self supported (aka [Self
    powered](https://www.tesla.com/en_gb/support/energy/powerwall/mobile-app/self-powered)
    or Self sufficiency). In this mode the Powerwall charges from
    solar, and tries to avoid using power from the electricity grid
    unless the load is more than the battery can support.

  - Autonomous (aka [Time based
    control](https://www.tesla.com/en_gb/support/energy/powerwall/mobile-app/time-based-control)).
    In this mode the Powerwall tries to optimise energy costs by
    charging the battery at off-peak (cheap) rates and powering your
    home at peak times. It may also load shift, exporting energy at
    peak times.

  - Backup[^2]. In this mode, 100% of the battery is reserved to power your
    house during a power cut.

* [Energy export
  mode](https://www.tesla.com/en_gb/support/energy/powerwall/mobile-app/advanced-settings#energy-exports-anchor).
  Can be one of:

  - Never. Avoid exporting energy to the grid.

  - PV only. Only export energy being produced by solar to the grid.

  - Battery ok. Exporting energy stored by the battery is allowed, as
    well as solar.

* [Grid
  charging](https://www.tesla.com/en_gb/support/energy/powerwall/mobile-app/advanced-settings#grid-charging-anchor).
  When on, the Powerwall is allowed to charge from the electricity
  grid. Otherwise it will only charge from solar.

[^1]: Backup reserve values must be between 0 and 80%, or 100%. Values
  between 81% and 99% will be treated as 80%. See the [Netzero
  update](https://docs.netzero.energy/docs/tesla/BackupReserveUpdate).

[^2]: Support for Backup mode was removed from the Tesla App. The
  Netzero API [still
  supports](https://docs.netzero.energy/docs/tesla/BackupMode) setting
  this mode.

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
installed from source. HACS is not aware of this integration yet.

Download the latest
[release](https://github.com/kilroyd/powerwall_control/releases) from
Github.

Copy the subdirectory custom_components/powerwall_control to your Home
Assistant server's &lt;config&gt;/custom_components directory.

    cp -r powerwall_control/custom_components/powerwall_control \
          $HOME_ASSIST_CONFIG_DIR/custom_components/.

# Setup

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

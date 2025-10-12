# Overview

The [Tesla Powerwall](https://www.tesla.com/powerwall) [Home Assistant
integration](https://www.home-assistant.io/integrations/powerwall/)
allows you to get Powerwall status from the Tesla cloud. However it
doesn't provide any control over the Powerwall.

This integration uses the [Netzero App](https://www.netzero.energy)
[Developer API](https://docs.netzero.energy/docs/tesla/API) to control
the Powerwall. Use of the Developer API is free. The Netzero App
supports a number of features (automation, monitorring, diagnostics)
via subscription - if you have a Powerwall and/or Tesla consider
subscribing.

The benefit of this setup is that you just need an API Token and
System ID from Netzero - there's no need to configure publicly
available credentials.

# Setup

* Download the Netzero App onto your phone from the Apple store or the
  Google Play Store as appropriate.

* Sign into the Netzero App with your Tesla username and password.

* Separately sign into your Tesla account (not in the Tesla App), and
  approve access for the Netzero App. They will appear under the
  Manage Access page as a third party.

* The free Netzero Basic subscription is sufficient.

* In the Netzero App, go to Settings->Developer API.

* Take a note of the API Token and System ID.

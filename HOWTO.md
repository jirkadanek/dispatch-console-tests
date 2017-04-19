Webdriver is a nickname for Selenium 2, used by people who want to explicitly distinguish it from Selenium RC.

# Headless testing

Either run a headless version of browser (PhantomJS, headless Chromium) or a headless version of Xserver with normal browser http://stackoverflow.com/questions/19127641/xvfb-install-on-linux  (https://en.wikipedia.org/wiki/Xvfb , http://xpra.org/trac/wiki/Xdummy )

# Good practices

https://mestachs.wordpress.com/2012/08/13/selenium-best-practices/
http://sauceio.com/index.php/2015/04/recap-practical-tips-tricks-for-selenium-test-automation/
http://googletesting.blogspot.cz/2009/06/my-selenium-tests-arent-stable.html

## Visual testing

Takes full page screenshots and compares with previous run. Displays diffs. If sophisticated, diffs are not affected by resolution changes, rasterization differences and so on. If changes are detected, it alerts the tester, who approves change or raises a bug. https://www.youtube.com/watch?v=CHUuLdkFfm0 (has a slide with a list of tools)

## Using Page objects

Page object encapsulates a page and provides methods for interacting with it. If a page changes, only a page object needs to change, testing code using the page object stays the same.

http://martinfowler.com/bliki/PageObject.html
http://selenium-python.readthedocs.io/page-objects.html

Examples: [Google: Tuesday Closing Keynote - YouTube](https://www.youtube.com/watch?v=cSLmfegT36A) [Facebook: Stable, Useful, Easy. Pick Three. - YouTube](https://youtu.be/7tzA2nsg1jQ?t=14m) // TODO: get a screenshot of the relevant slide or copy the code.

## Avoid PhantomJS 2

According to https://github.com/detro/ghostdriver​, PhantomJS 2 for Webdriver is not really maintained. I (jdanek) am a whitness to this, ghostdriver author suggests https://github.com/MachinePublishers/jBrowserDriver/

## Waiting for page to load

Pick element that is present on the new page and not on the old one and wait for it to appear, http://www.obeythetestinggoat.com/how-to-get-selenium-to-wait-for-page-load-after-a-click.html

## Teams using webdriver

This friend of Tomas' writes Webdriver tests in nightwatchjs.org, not sure what product it is.

// TODO

HAWKULAR-185 Add IDs for selenium to be able to log out (for QA) by Jiri-Kremser · Pull Request #106 · hawkular/hawkular… Interesting discussions by devs reluctant to add IDs on page elements.

# See also

The testing pyramid idea, http://martinfowler.com/bliki/TestPyramid.html , http://googletesting.blogspot.cz/2015/04/just-say-no-to-more-end-to-end-tests.html . Do only a "submit an empty form" and "submit correctly filled form" scenarios in Webdriver and test the rest through Karma or other in-page JS test runner / through HTTP client, if that is appropriate for Hawtio, meaning if Hawtio has some Json API the page uses.
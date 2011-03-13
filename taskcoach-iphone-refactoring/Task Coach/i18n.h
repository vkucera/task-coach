
#ifndef _I18N_H_
#define _I18N_H_

// So I can use the GNU gettext utilities to get standard message files for Launchpad.

#define _(x) NSLocalizedString(@x, @__FILE__)

#endif

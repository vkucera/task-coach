/*
 *  LogUtils.h
 *  TaskCoach
 *
 *  Created by Jérôme Laheurte on 10/07/10.
 *  Copyright 2010 Jérôme Laheurte. All rights reserved.
 *
 */

#ifndef _LOGUTILS_H_
#define _LOGUTILS_H_

#import "DateUtils.h"

#define LOGLEVEL_INFO         0
#define LOGLEVEL_DEBUG        1
#define LOGLEVEL_WARN         2
#define LOGLEVEL_ERROR        3

void LogCreateFile(void);
const char *LogFilename(void);

void LogSetLevel(unsigned int level);
void LogMessage(unsigned int level, const char *fmt, ...);

#define JLMSG(level, fmt, args...) do { \
  NSLog([NSString stringWithUTF8String:"%s: " fmt], __FUNCTION__, ## args); \
  LogMessage(level, "%s [%s]: " fmt "\n", [[[TimeUtils instance] stringFromDate:[NSDate date]] UTF8String], __FUNCTION__, ## args); \
} while (0)

#define JLINFO(fmt, args...) JLMSG(LOGLEVEL_INFO, fmt, ## args)
#define JLDEBUG(fmt, args...) JLMSG(LOGLEVEL_DEBUG, fmt, ## args)
#define JLWARN(fmt, args...) JLMSG(LOGLEVEL_WARN, fmt, ## args)
#define JLERROR(fmt, args...) JLMSG(LOGLEVEL_ERROR, fmt, ## args)

#endif

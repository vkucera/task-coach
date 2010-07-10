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

#define LOGLEVEL_INFO         0
#define LOGLEVEL_DEBUG        1
#define LOGLEVEL_WARN         2
#define LOGLEVEL_ERROR        3

void LogCreateFile(void);
const char *LogFilename(void);

void LogSetLevel(unsigned int level);
void LogMessage(unsigned int level, const char *fmt, ...);

#define JLINFO(fmt, args...) LogMessage(LOGLEVEL_INFO, fmt "\n", ## args)
#define JLDEBUG(fmt, args...) LogMessage(LOGLEVEL_DEBUG, fmt "\n", ## args)
#define JLWARN(fmt, args...) LogMessage(LOGLEVEL_WARN, fmt "\n", ## args)
#define JLERROR(fmt, args...) LogMessage(LOGLEVEL_ERROR, fmt "\n", ## args)

#endif

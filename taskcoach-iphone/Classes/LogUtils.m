/*
 *  LogUtils.m
 *  TaskCoach
 *
 *  Created by Jérôme Laheurte on 10/07/10.
 *  Copyright 2010 Jérôme Laheurte. All rights reserved.
 *
 */

#import <unistd.h>

#import "LogUtils.h"
#import "TaskCoachAppDelegate.h"

static unsigned int _level = 
#ifdef DEBUG
LOGLEVEL_INFO
#else
LOGLEVEL_ERROR
#endif
;

static char *_logPath = NULL;

void LogCreateFile(void)
{
	if (_logPath)
	{
		free(_logPath);
		_logPath = NULL;
	}

	NSString *path = [[(TaskCoachAppDelegate *)[UIApplication sharedApplication].delegate applicationDocumentsDirectory] stringByAppendingPathComponent: @"Log.txt"];
	_logPath = strdup([path UTF8String]);

	unlink(_logPath);
}

const char *LogFilename(void)
{
	return _logPath;
}

void LogSetLevel(unsigned int level)
{
	_level = level;
}

void LogMessage(unsigned int level, const char *fmt, ...)
{
	if ((level >= _level) && _logPath)
	{
		FILE *fp = fopen(_logPath, "a+");
		va_list ls;
		va_start(ls, fmt);
		vfprintf(fp, fmt, ls);
		va_end(ls);
		fclose(fp);
	}
}

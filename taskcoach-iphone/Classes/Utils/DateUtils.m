//
//  DateUtils.m
//  TaskCoach
//
//  Created by Jérôme Laheurte on 19/01/09.
//  Copyright 2009 Jérôme Laheurte. See COPYING for details.
//

#import "DateUtils.h"

static DateUtils *_dinstance = NULL;
static TimeUtils *_tinstance = NULL;
static UserTimeUtils *_uinstance = NULL;

@implementation DateUtils

+ (DateUtils *)instance
{
	if (!_dinstance)
		_dinstance = [[DateUtils alloc] init];
	return _dinstance;
}

- init
{
	if (self = [super init])
	{
		[self setDateFormat:@"yyyy-MM-dd"];
	}
	
	return self;
}

@end

@implementation TimeUtils

+ (TimeUtils *)instance
{
	if (!_tinstance)
		_tinstance = [[TimeUtils alloc] init];
	return _tinstance;
}

- init
{
	if (self = [super init])
	{
		[self setDateFormat:@"yyyy-MM-dd HH:mm:ss"];
	}

	return self;
}

@end

@implementation UserTimeUtils

+ (UserTimeUtils *)instance
{
	if (!_uinstance)
		_uinstance = [[UserTimeUtils alloc] init];
	return _uinstance;
}

- init
{
	if (self = [super init])
	{
		[self setDateStyle:NSDateFormatterShortStyle];
		[self setTimeStyle:NSDateFormatterShortStyle];
	}
	
	return self;
}

@end

//
//  DateUtils.m
//  TaskCoach
//
//  Created by Jérôme Laheurte on 19/01/09.
//  Copyright 2009 Jérôme Laheurte. See COPYING for details.
//

#import "DateUtils.h"

static DateUtils *_instance = NULL;

@implementation DateUtils

+ (DateUtils *)instance
{
	if (!_instance)
		_instance = [[DateUtils alloc] init];
	return _instance;
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

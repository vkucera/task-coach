//
//  NSDate+Utils.m
//  TaskCoach
//
//  Created by Jérôme Laheurte on 09/05/10.
//  Copyright 2010 Jérôme Laheurte. All rights reserved.
//

#import "NSDateUtils.h"


@implementation NSDateUtils

// This used to be a category on NSDate but it doesn't work anymore...

+ (NSDate *)dateRoundedTo:(NSInteger)round
{
	return [NSDate dateWithTimeIntervalSinceReferenceDate:round * 60 + round *
            60 * floor([[NSDate date] timeIntervalSinceReferenceDate] /
                       round / 60)];
}

@end

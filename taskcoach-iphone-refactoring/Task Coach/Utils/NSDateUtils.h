//
//  NSDate+Utils.h
//  TaskCoach
//
//  Created by Jérôme Laheurte on 09/05/10.
//  Copyright 2010 Jérôme Laheurte. All rights reserved.
//

#import <Foundation/Foundation.h>


@interface NSDateUtils : NSObject

// Current date, rounded to the minute start
+ (NSDate *)dateRoundedTo:(NSInteger)round;

@end

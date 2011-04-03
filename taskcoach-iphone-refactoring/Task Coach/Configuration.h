//
//  Configuration.h
//  Task Coach
//
//  Created by Jérôme Laheurte on 13/03/11.
//  Copyright 2011 __MyCompanyName__. All rights reserved.
//

#import <Foundation/Foundation.h>

#import "CDList.h"

#define GROUPING_STATUS      0
#define GROUPING_PRIORITY    1
#define GROUPING_START       2
#define GROUPING_DUE         3

/*
@interface TaskStatusSection : NSObject
{
    NSString *condition;
    BOOL displayed;
}

@property (nonatomic, readonly) NSString *condition;
@property (nonatomic) BOOL displayed;

@end
 */

@interface Configuration : NSObject
{
    NSURL *currentListURL;
    NSInteger soonDays;
    NSInteger grouping;
    BOOL revertGrouping;

    // NSArray *sections;
}

+ (Configuration *)instance;

- (void)save;

@property (copy) CDList *currentList;
@property () NSInteger soonDays;
@property () NSInteger grouping;
@property (readonly) NSString *groupingName;
@property () BOOL revertGrouping;

// @property (nonatomic, copy) NSArray *sections;

@end

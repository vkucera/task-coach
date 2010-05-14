//
//  Configuration.h
//  TaskCoach
//
//  Created by Jérôme Laheurte on 17/01/09.
//  Copyright 2009 Jérôme Laheurte. See COPYING for details.
//

#import <Foundation/Foundation.h>

#define ICONPOSITION_RIGHT 0
#define ICONPOSITION_LEFT  1

#define STYLE_TABLE    0
#define STYLE_CALENDAR 1

@interface Configuration : NSObject
{
	BOOL showCompleted;
	NSInteger iconPosition;
	BOOL compactTasks;
	BOOL confirmComplete;
	
	NSInteger soonDays;

	NSString *name;
	NSString *domain;

	NSInteger viewStyle;
}

@property (nonatomic, readonly) BOOL showCompleted;
@property (nonatomic, readonly) NSInteger iconPosition;
@property (nonatomic, readonly) BOOL compactTasks;
@property (nonatomic, readonly) BOOL confirmComplete;
@property (nonatomic, readonly) NSInteger soonDays;
@property (nonatomic, copy) NSString *name;
@property (nonatomic, copy) NSString *domain;
@property (nonatomic) NSInteger viewStyle;

+ (Configuration *)configuration;
- (void)save;

@end

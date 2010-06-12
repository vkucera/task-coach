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

#define GROUP_STATUS   0
#define GROUP_PRIORITY 1
#define GROUP_START    2
#define GROUP_DUE      3

@class CDFile;

@interface Configuration : NSObject
{
	BOOL showCompleted;
	BOOL showInactive;
	NSInteger iconPosition;
	BOOL compactTasks;
	BOOL confirmComplete;
	
	NSInteger soonDays;

	NSString *name;
	NSString *domain;

	NSInteger viewStyle;

	CDFile *cdCurrentFile;

	NSInteger taskGrouping;
}

@property (nonatomic, readonly) BOOL showCompleted;
@property (nonatomic, readonly) BOOL showInactive;
@property (nonatomic, readonly) NSInteger iconPosition;
@property (nonatomic, readonly) BOOL compactTasks;
@property (nonatomic, readonly) BOOL confirmComplete;
@property (nonatomic, readonly) NSInteger soonDays;
@property (nonatomic, copy) NSString *name;
@property (nonatomic, copy) NSString *domain;
@property (nonatomic) NSInteger viewStyle;
@property (nonatomic) NSInteger taskGrouping;

@property (nonatomic, retain) CDFile *cdCurrentFile;
@property (nonatomic, readonly) NSInteger cdFileCount;

+ (Configuration *)configuration;
- (void)save;

@end

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

	NSString *currentFileGuid;

	NSInteger taskGrouping;
	BOOL reverseGrouping;
}

@property (nonatomic) BOOL showCompleted;
@property (nonatomic) BOOL showInactive;
@property (nonatomic) NSInteger iconPosition;
@property (nonatomic) BOOL compactTasks;
@property (nonatomic) BOOL confirmComplete;
@property (nonatomic, readonly) NSInteger soonDays;
@property (nonatomic, copy) NSString *name;
@property (nonatomic, copy) NSString *domain;
@property (nonatomic) NSInteger taskGrouping;
@property (nonatomic) BOOL reverseGrouping;

@property (nonatomic, assign) CDFile *cdCurrentFile;
@property (nonatomic, readonly) NSInteger cdFileCount;

+ (Configuration *)configuration;
- (void)save;

@end

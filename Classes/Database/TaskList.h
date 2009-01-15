//
//  TaskList.h
//  TaskCoach
//
//  Created by Jérôme Laheurte on 15/01/09.
//  Copyright 2009 __MyCompanyName__. All rights reserved.
//

#import <Foundation/Foundation.h>

@class Statement;
@class Task;

@interface TaskList : NSObject
{
	NSMutableArray *tasks;
	NSInteger firstIndex;
	Statement *request;
	NSInteger count;
}

@property (nonatomic, readonly) NSInteger count;

- initWithView:(NSString *)viewName category:(NSInteger)categoryId;

- (Task *)taskAtIndex:(NSInteger)index;
- (void)reload;

@end

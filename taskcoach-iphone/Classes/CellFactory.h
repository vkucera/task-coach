//
//  CellFactory.h
//  TaskCoach
//
//  Created by Jérôme Laheurte on 17/01/09.
//  Copyright 2009 __MyCompanyName__. All rights reserved.
//

#import <Foundation/Foundation.h>

@class TaskCell;

@interface CellFactory : NSObject
{
	TaskCell *taskCellTemplate;
}

@property (nonatomic, assign) IBOutlet TaskCell *taskCellTemplate;

+ (CellFactory *)cellFactory;

- (TaskCell *)createTaskCell;

@end

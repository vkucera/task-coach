//
//  TaskCellFactory.h
//  Task Coach
//
//  Created by Jérôme Laheurte on 03/04/11.
//  Copyright 2011 __MyCompanyName__. All rights reserved.
//

#import <Foundation/Foundation.h>

#import "TaskCell.h"

@interface TaskCellFactory : NSObject
{
    IBOutlet TaskCell *template;
}

+ (TaskCellFactory *)instance;

- (TaskCell *)create;

@end

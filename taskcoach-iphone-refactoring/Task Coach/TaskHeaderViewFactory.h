//
//  TaskHeaderViewFactory.h
//  Task Coach
//
//  Created by Jérôme Laheurte on 03/04/11.
//  Copyright 2011 __MyCompanyName__. All rights reserved.
//

#import <Foundation/Foundation.h>

#import "TaskHeaderView.h"

@interface TaskHeaderViewFactory : NSObject
{
    IBOutlet TaskHeaderView *template;
}

+ (TaskHeaderViewFactory *)instance;

- (TaskHeaderView *)create;

@end

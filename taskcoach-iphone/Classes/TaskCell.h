//
//  TaskCell.h
//  TaskCoach
//
//  Created by Jérôme Laheurte on 17/01/09.
//  Copyright 2009 __MyCompanyName__. All rights reserved.
//

#import <UIKit/UIKit.h>

@class Task;

@interface TaskCell : UITableViewCell
{
	UIImageView *leftImage;
	UILabel *titleLabel;
	UILabel *infosLabel;
}

@property (nonatomic, retain) IBOutlet UIImageView *leftImage;
@property (nonatomic, retain) IBOutlet UILabel *titleLabel;
@property (nonatomic, retain) IBOutlet UILabel *infosLabel;

- (void)setTask:(Task *)task;

@end
